import copy
import sys, os
import csv
from tqdm import tqdm
from os.path import exists
from registration import overlap
from registration.overlap import OverlapType, AlignmentType


MEMBERSHIP_THRESHOLD = 0.5

# determines if BY/CY pair has joint alignment
JOINT_THRESHOLD = 400

# Percentage of BY slab length that must be replaced to count as an R slab
REPLACED_THRESHOLD = 0.25

class SlabRegistration:
    def __init__(self, slab_inventory, seg_str: str, data_dir: str, mode: str,
                 by: int, years: list, first_slabs: list):
        self.slab_inventory = slab_inventory
        
        self.minslablength = 100
        self.data_dir = data_dir
        self.possiblyor = 2
        self.seg_str = seg_str
        self.interval = 1220 # 1220 mm = 4 feet
        self.endbuffer = 610 # 610 mm = 2 feet  
        self.years = years
        self.first_slabs = first_slabs
        self.by = by
        self.mode = mode
        self.prompt_input()
        by_start_slab = self.first_slabs[self.years.index(self.by)]
        self.by_slabs = list(self.slab_inventory.get_year_slab_data(seg_str,
            self.by, by_start_slab))
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
        self.majority_slabs = [{str(self.by): x['slab_index']} 
                               for x in self.by_slabs]
        
        
    def register(self, progress_bar=None):
        """Carries out registration for each year.

        Args:
            progress_bar (QProgressBar, optional): Progress bar to update. 
            Defaults to None.
        """
        self.slab_inventory.create_registration_entry(self.seg_str, self.by, 
                                                      self.years)
        for year, first_slab in zip(self.years, self.first_slabs):
            # self.align_year(year, first_slab)
            if year != self.by: 
                self.categorize_by_length(year, first_slab)
        self.slab_inventory.update_registration_data(self.reg_data, 
                                                     self.seg_str, 
                                                     self.by, 
                                                     self.years)
        if self.mode == 'single':
            self.build_single_spreadsheet(progress_bar=progress_bar)
        else:
            self.build_single_spreadsheet(progress_bar=progress_bar, 
                                          avg_faulting=True)



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


    # def align_year(self, year: int, first_slab: int):
    #     """Aligns the starting point of the slabs in a year to the starting slab
    #     specified.

    #     Args:
    #         year (int): year to align
    #         first_slab (int): first slab index, its offset will be set to 0 and 
    #         all other slabs in the year will be adjusted accordingly
    #     """
    #     slab_data = self.slab_inventory.get_slab_data(
    #         year, first_slab, self.seg_str)
    #     shift = -(slab_data['y_offset'])
    #     self.writer.update_offsets(year, shift)


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
        cy_slabs = list(self.slab_inventory.get_year_slab_data(
            self.seg_str, year, first_slab))
        self.reg_data[0][str(year)] = []   
        cy_entries = self.reg_data[0][str(year)]
        # indices for the BY and CY slabs
        byi, cyi = 0, 0
        cy_rel_offset = 0
        # keep track of CY joint alignments for each BY slab
        exterior = interior = aligned = 0
        new_BY = True
        max_overlap = -1
        while byi < len(self.by_slabs) and cyi < len(cy_slabs):

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
            if (overlap_type == OverlapType.FULL_OVERLAP or 
                overlap_type == OverlapType.BASE_MAJORITY_OVERLAP or
                overlap_type == OverlapType.CURRENT_MAJORITY_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])
                
                overlap_percentage = overlap.percent_BY_overlap(0, 
                                                                by_length, 
                                                                cy_rel_offset, 
                                                                cy_length)
                
                if overlap_percentage > max_overlap:
                    max_overlap = overlap_percentage
                    self.majority_slabs[byi][str(year)] = \
                        cy_slabs[cyi]['slab_index']


            if new_BY:
                # left CY joint out of bounds of BY slab
                if cy_rel_offset < -JOINT_THRESHOLD:
                    exterior += 1
                # Left CY joint in bounds of BY slab
                elif cy_rel_offset > JOINT_THRESHOLD:
                    interior += 1
                # Left CY joint aligned with BY slab
                else:
                    aligned += 1
                new_BY = False

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

            # if 1920 <= cyi <= 1927:
            #     print(f'Interior: {interior}, Exterior: {exterior}, Aligned: {aligned}\n')

            # BY slab ends at or before the CY slab
            if by_length < cy_length + cy_rel_offset + JOINT_THRESHOLD:
                new_BY = True
                existing_rep_year = self.reg_data[byi]['replaced']  
                rep_type = overlap.replacement_type(interior, exterior, aligned,
                                                    cy_length, by_length, 
                                                    cy_rel_offset, 
                                                    REPLACED_THRESHOLD)
                
                if (not existing_rep_year and 
                    rep_type != AlignmentType.FULL_TWO_ALIGN):

                    self.reg_data[byi]['replaced_type'] = rep_type.name
                    self.reg_data[byi]['interior'] = interior
                    self.reg_data[byi]['exterior'] = exterior
                    self.reg_data[byi]['aligned'] = aligned

                    if rep_type != AlignmentType.JOINT_REPLACEMENT:
                        self.reg_data[byi]['replaced'] = year
                interior = exterior = aligned = 0
                max_overlap = -1
                byi += 1
                if byi < len(self.by_slabs):
                    self.reg_data[byi][str(year)] = []
                    cy_entries = self.reg_data[byi][str(year)]

                # BY and CY slabs end at same point, also visit next CY slab
                if abs(by_length - (cy_length + cy_rel_offset)) < JOINT_THRESHOLD:
                    cy_rel_offset = 0
                    cyi += 1
                else:
                    cy_rel_offset -= by_length
            # cy slab ends before by slab, go to next cy slab, so offset of the
            # cy slab relative to the by slab is recalibrated
            else:
                cy_rel_offset += cy_length
                cyi += 1
    

    def build_single_spreadsheet(self, progress_bar=None, 
                                 avg_faulting=False):
        """Builds a single spreadsheet with all the registration data. The 
        single associating slab in the CY is the one that has the most overlap
        with the BY slab. If the avg_faulting flag is set to True, then all 
        CY slabs' faulting values that are associated with the BY slab will be
        averaged together instead of just using the CY slab with the majority 
        overlap.

        Args:
            progress_bar (QProgressBar, optional): Progress bar to update.
            avg_faulting (bool, optional): If True, the average faulting of the
            CY slabs will be calculated. Defaults to False.
        """
        if progress_bar:
            progress_bar.setVisible(True)   
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(len(self.reg_data))
            progress_bar.setValue(0)
        metadata = self.seg_str.split('_')
        interstate = metadata[0]
        beginMM = int(metadata[1][2:])
        csv_name = (
            f'{self.seg_str}_{self.years[0]}_{self.years[-1]}_single.csv')
        spread_path = os.path.join(self.data_dir, csv_name)
        with open(spread_path, "w", newline="") as csv_file:
            fields = ['interstate', 'direction', 'MP_from', 'MP_to', 'BY_id',
                      'BY_length (ft)']
            for year in self.years:
                fields.append(f'{year}_state')
            for year in self.years:
                fields.append(f'{year}_faulting')
            
            curr_MP = beginMM
            fields.extend(['year_replaced', 'replaced_type'])
            writer = csv.DictWriter(csv_file, fieldnames=fields)    
            writer.writeheader()
            i_name = interstate[0:-2]
            direction = interstate[-2:].upper()
            for i, entry in tqdm(enumerate(self.reg_data), 
                                 total=len(self.reg_data)):
                row_dict = {'interstate': i_name, 
                            'direction': direction,
                            'year_replaced': entry['replaced'],
                            'replaced_type': entry['replaced_type']}
                for year in self.years:
                    yr_slab = None
                    if str(year) in self.majority_slabs[i]:
                        yr_id = self.majority_slabs[i][str(year)]
                        yr_slab = self.slab_inventory.fetch_slab(
                            year, yr_id, self.seg_str)
                        row_dict[f'{year}_state'] = yr_slab['primary_state']
                        row_dict[f'{year}_faulting'] = (
                            self.avg_faulting_BY(i, year) if avg_faulting
                            else yr_slab['mean_faulting']
                            )
                    if year == self.by:
                        row_dict['BY_id'] = yr_id
                        row_dict['BY_length (ft)'] = round(yr_slab['length'] / 
                                                           304.8, 2)
                        row_dict['MP_from'] = curr_MP
                        curr_MP += (round(yr_slab['length'] / 1609000, 5) 
                                    if direction in ['NB', 'EB'] 
                                    else -round(yr_slab['length'] / 1609000, 5))
                        row_dict['MP_to'] = curr_MP
                writer.writerow(row_dict)
                if progress_bar:
                    progress_bar.setValue(i + 1)
        

    def avg_faulting_BY(self, byi, year):
        """Calculates the average faulting of a BY slab. Uses the base year 
        index (zero-indexed, representing the i-th BY slab in the list of BY)

        Args:
            byi (int): index of the BY slab
            year (int): year of the CY slabs to look at

        Returns:
            float: average faulting of the BY slab
        """
        total = 0
        count = 0
        cy_slab_ids = self.reg_data[byi][str(year)]
        for cy_id in cy_slab_ids:
            slab = self.slab_inventory.fetch_slab(year, cy_id, self.seg_str)
            if slab['mean_faulting']:
                total += slab['mean_faulting']
                count += 1

        if total == 0:
            return None
        return total / count

                    



    

