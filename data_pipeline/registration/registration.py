import copy
import sys, os
from os.path import exists
from db_operation.registration_writer import RegistrationWriter
from registration import overlap
from registration.overlap import OverlapType, AlignmentType


MEMBERSHIP_THRESHOLD = 0.5

# 610 mm = 2 feet, determines if BY/CY pair has joint alignment
JOINT_THRESHOLD = 610 

# Percentage of BY slab length that must be replaced to count as an R slab
REPLACED_THRESHOLD = 0.25

class SlabRegistration:
    def __init__(self, beginMM: int, endMM: int, interstate: str):
        self.minslablength = 100
        self.possiblyor = 2
        self.interval = 1220 # 1220 mm = 4 feet
        self.endbuffer = 610 # 610 mm = 2 feet  
        self.years = None
        self.first_slabs = None
        self.by = None
        self.prompt_input()
        by_start_slab = self.first_slabs[self.years.index(self.by)]
        self.writer = RegistrationWriter(beginMM, endMM, interstate, self.by, self.years)
        self.by_slabs = list(self.writer.get_year_slab_data(self.by, by_start_slab))
        self.reg_data = [
            {
                "base_id": x['slab_index'], 
                "replaced": None,
                "replaced_type": None,
                "interior": 0,
                "exterior": 0,
                "aligned": 2,
                str(self.by): [x['slab_index']]
            } 
            for x in self.by_slabs
            ]
        print("Running code...")
        self.register()
        self.writer.update_registration_data(self.reg_data)
       

        
    def register(self):
        """Carries out registration for each year.
        """
        for year, first_slab in zip(self.years, self.first_slabs):
            self.align_year(year, first_slab)
            if year != self.by: 
                self.categorize_by_length(year, first_slab)



    def prompt_input(self):
        """Prompts user to input the years they want to register, as well as the
        base year to align by and the first slab index for each year to align
        by.
        """
        while self.years == None:
            years_input = input("Enter years from least to greatest, separate "
                                "them with a comma (ex. 2014, 2015, 2017):\n"
                                ).split(", ")
            try: 
                self.years = [int(x) for x in years_input]
            except:
                None
        
        while self.by not in self.years:
            try:
                self.by = int(input("Enter base year, this should be a year "
                                    "within the list inputed previously:\n"))
            except:
                None
        
        while (self.first_slabs == None 
               or len(self.first_slabs) != len(self.years)):
            first_slabs_input = input("Enter the first slab index for each "
                                      "year to align by, separate them with a "
                                      "comma (ex. 1, 3, 5):\n").split(", ")
            try:
                self.first_slabs = [int(x) for x in first_slabs_input]
            except:
                None


    def align_year(self, year: int, first_slab: int):
        """Aligns the starting point of the slabs in a year to the starting slab
        specified.

        Args:
            year (int): year to align
            first_slab (int): first slab index, its offset will be set to 0 and 
            all other slabs in the year will be adjusted accordingly
        """
        slab_data = self.writer.get_slab_data(year, first_slab)
        shift = -(slab_data['y_offset'])
        self.writer.update_offsets(year, shift)


    def categorize_by_length(self, year: int, first_slab: int): 
        """
        Goes through every BY/CY overlapping pair and determines if the pair 
        should be associated with each other based on length. Also detects
        misalignment and predicts the type of replacement that was done to a
        specific BY slab.

        Args:
            year (int): CY year to categorize
            first_slab (int): first slab index of the year
        """
        # list of current slabs
        cy_slabs = list(self.writer.get_year_slab_data(year, first_slab))
        self.reg_data[0][str(year)] = []   
        cy_entries = self.reg_data[0][str(year)]
        byi, cyi = 0, 0
        cy_rel_offset = 0
        while byi < len(self.by_slabs) and cyi < len(cy_slabs):
            # WARNINGS
            if byi >= len(self.by_slabs) + 1:
                raise Exception(f"Stopped when processing slab "
                                f"{cy_slabs[cyi]['slab_index']} of year "
                                f"{year}. Summation on total slab lengths "
                                f"between {self.by} and {year} do not match."
                                )

            by_length = self.by_slabs[byi]['length']
            cy_length = cy_slabs[cyi]['length']
            overlap_type = overlap.belongs_to(0, by_length, 
                                              cy_rel_offset, cy_length, 
                                              MEMBERSHIP_THRESHOLD)

            # Check membership
            if (overlap_type == OverlapType.FULL_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])
            elif (overlap_type == OverlapType.BASE_MAJORITY_OVERLAP or
                    overlap_type == OverlapType.CURRENT_MAJORITY_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])

            interior = exterior = aligned = 0
            # left CY joint out of bounds of BY slab
            if cy_rel_offset < -JOINT_THRESHOLD:
                exterior += 1
            # Left CY joint in bounds of BY slab
            elif cy_rel_offset > JOINT_THRESHOLD:
                interior += 1
            # Left CY joint aligned with BY slab
            else:
                aligned += 1

            CY_right = cy_rel_offset + cy_length
            # Right CY joint out of bounds of BY slab
            if CY_right > by_length + JOINT_THRESHOLD:
                exterior += 1
            # Right CY joint in bounds of BY slab
            elif CY_right < by_length - JOINT_THRESHOLD:
                interior += 1
            # Right CY joint aligned with BY slab
            else:
                aligned += 1

            rep_type = overlap.replacement_type(interior, exterior, aligned)
            
            existing_rep_year = self.reg_data[byi]['replaced']
            existing_alignment = self.reg_data[byi]['replaced_type']
            if existing_rep_year and existing_rep_year < year:
                pass
            elif rep_type == AlignmentType.FULL_TWO_ALIGN:
                pass
            elif (not existing_alignment 
                  or rep_type.value > AlignmentType[existing_alignment].value):
                if rep_type == AlignmentType.PARTIAL_EXTERIOR:
                    if overlap.percent_BY_overlap(0, 
                                                by_length, 
                                                cy_rel_offset, 
                                                cy_length) > REPLACED_THRESHOLD:
                        self.reg_data[byi]['replaced'] = year
                        self.reg_data[byi]['replaced_type'] = rep_type.name
                    elif cy_length < 1900:
                        self.reg_data[byi]['replaced_type'] = 'JOINT_REPLACEMENT'
                        self.reg_data[byi]['replaced'] = None
                else:
                    self.reg_data[byi]['replaced'] = year
                    self.reg_data[byi]['replaced_type'] = rep_type.name
                self.reg_data[byi]['interior'] = interior  
                self.reg_data[byi]['exterior'] = exterior
                self.reg_data[byi]['aligned'] = aligned

        
            


            # slabs end at the same point, recalibrate relative offset
            if abs(by_length - (cy_length + cy_rel_offset)) < self.interval:
                cy_rel_offset = 0
                byi += 1
                if byi < len(self.by_slabs):
                    self.reg_data[byi][str(year)] = []
                    cy_entries = self.reg_data[byi][str(year)]
                cyi += 1
            # by slab ends before cy slab, go to next by slab, so offset of the
            # cy slab relative to the by slab is recalibrated
            elif by_length < cy_length + cy_rel_offset:
                cy_rel_offset -= by_length
                byi += 1
                if byi < len(self.by_slabs):
                    self.reg_data[byi][str(year)] = []
                    cy_entries = self.reg_data[byi][str(year)]
            # cy slab ends before by slab, go to next cy slab, so offset of the
            # cy slab relative to the by slab is recalibrated
            else:
                cy_rel_offset += cy_length
                cyi += 1
    
    

