import copy
import sys, os
from os.path import exists
from db_operation.registration_writer import RegistrationWriter
from registration import overlap
from registration.overlap import OverlapType
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
                                              cy_rel_offset, cy_length)

            # Check membership
            if (overlap_type == OverlapType.FULL_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])
            elif (overlap_type == OverlapType.BASE_MAJORITY_OVERLAP or
                    overlap_type == OverlapType.CURRENT_MAJORITY_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])
                if self.reg_data[byi]["replaced"] == None:
                    self.reg_data[byi]["replaced"] = year

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
    
    

