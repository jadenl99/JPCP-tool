import copy
import sys, os
import csv
from tqdm import tqdm
from os.path import exists
from registration import overlap
from registration.overlap import OverlapType, AlignmentType
from PyQt5.QtCore import QObject, pyqtSignal

class SlabRegistration(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    progress_max = pyqtSignal(int)
    reset_progress = pyqtSignal()  
    
    def __init__(self, slab_inventory, seg_str: str, data_dir: str, mode: str,
                 by: int, years: list, first_slabs: list, 
                 include_replaced=True, include_intensity_replaced=False,
                 ratio: float = 0.5):
        super().__init__()
        self.slab_inventory = slab_inventory
        self.MEMBERSHIP_THRESHOLD = ratio
        # Percentage of BY slab length that must be replaced to count as an R slab
        self.REPLACED_THRESHOLD = ratio
        #print(ratio)
        # determines if BY/CY pair has joint alignment
        self.JOINT_THRESHOLD = 400 
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
        self.include_replaced = include_replaced
        self.include_intensity_replaced = include_intensity_replaced
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
        
        
    def run(self):
        """Carries out registration for each year.
        """
        self.slab_inventory.create_registration_entry(self.seg_str, self.by, 
                                                      self.years)
        for year, first_slab in zip(self.years, self.first_slabs):
            if year != self.by: 
                self.categorize_by_length(year, first_slab)
        self.slab_inventory.update_registration_data(self.reg_data, 
                                                     self.seg_str, 
                                                     self.by, 
                                                     self.years)
        if self.mode == 'single':
            self.build_single_spreadsheet(
                avg_faulting=False,
                include_replaced=self.include_replaced,
                include_intensity_replaced=self.include_intensity_replaced
                )
        else:
            self.build_single_spreadsheet(
                avg_faulting=True,
                include_replaced=self.include_replaced,
                include_intensity_replaced=self.include_intensity_replaced
                )
        self.finished.emit()


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
        replaced_ratio = 0
        replaced_slab_length = -1
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
                                              self.MEMBERSHIP_THRESHOLD)
            overlap_percentage = overlap.percent_BY_overlap(0, 
                                                            by_length, 
                                                            cy_rel_offset, 
                                                            cy_length)
            # Check membership
            if (overlap_type == OverlapType.FULL_OVERLAP or 
                overlap_type == OverlapType.BASE_MAJORITY_OVERLAP or
                overlap_type == OverlapType.CURRENT_MAJORITY_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['slab_index'])
                
                
                
                if overlap_percentage > max_overlap:
                    max_overlap = overlap_percentage
                    self.majority_slabs[byi][str(year)] = \
                        cy_slabs[cyi]['slab_index']


            if new_BY:
                # left CY joint out of bounds of BY slab
                if cy_rel_offset < -self.JOINT_THRESHOLD:
                    exterior += 1
                    if overlap_percentage > replaced_ratio:
                        replaced_ratio += overlap_percentage
                        replaced_slab_length = cy_length
                # Left CY joint in bounds of BY slab
                elif cy_rel_offset > self.JOINT_THRESHOLD:
                    interior += 1
                # Left CY joint aligned with BY slab
                else:
                    aligned += 1
                new_BY = False
           
            CY_right = cy_rel_offset + cy_length
            # Right CY joint out of bounds of BY slab
            if CY_right > by_length + self.JOINT_THRESHOLD:
                exterior += 1
                if overlap_percentage > replaced_ratio:
                    replaced_ratio += overlap_percentage
                    replaced_slab_length = cy_length
            # Right CY joint in bounds of BY slab
            elif CY_right < by_length - self.JOINT_THRESHOLD:
                interior += 1
            # Right CY joint aligned with BY slab
            else:
                aligned += 1

            if by_length < cy_length + cy_rel_offset + self.JOINT_THRESHOLD:
                new_BY = True
                existing_rep_year = self.reg_data[byi]['replaced']  
                rep_type = overlap.replacement_type(interior, exterior, aligned,
                                                    replaced_slab_length, 
                                                    replaced_ratio, 
                                                    self.REPLACED_THRESHOLD)
                
                if existing_rep_year:
                    # mark slab as R
                    # for index in cy_entries:
                    #     self.slab_inventory.add_slab_update_request(
                    #         year, index, {'special_state': 'R'}, self.seg_str
                    #     )
                    pass
                if (not existing_rep_year and 
                    rep_type != AlignmentType.FULL_TWO_ALIGN):
                    print(f'BY: {self.by}, byi: {byi}, ratio: {replaced_ratio}, type: {rep_type}')
                    self.reg_data[byi]['replaced_type'] = rep_type.name
                    self.reg_data[byi]['interior'] = interior
                    self.reg_data[byi]['exterior'] = exterior
                    self.reg_data[byi]['aligned'] = aligned

                    if rep_type != AlignmentType.JOINT_REPLACEMENT:
                        self.reg_data[byi]['replaced'] = year
                        # mark slab as R
                        for index in cy_entries:
                            self.slab_inventory.add_slab_update_request(
                                year, index, {'special_state': 'R'}, self.seg_str
                            )
                interior = exterior = aligned = 0
                max_overlap = -1
                replaced_ratio = 0
                replaced_slab_length = -1
                byi += 1
                if byi < len(self.by_slabs):
                    self.reg_data[byi][str(year)] = []
                    cy_entries = self.reg_data[byi][str(year)]

                # BY and CY slabs end at same point, also visit next CY slab
                if abs(by_length - (cy_length + cy_rel_offset)) < self.JOINT_THRESHOLD:
                    cy_rel_offset = 0
                    cyi += 1
                else:
                    cy_rel_offset -= by_length
            # cy slab ends before by slab, go to next cy slab, so offset of the
            # cy slab relative to the by slab is recalibrated
            else:
                cy_rel_offset += cy_length
                cyi += 1
        self.slab_inventory.execute_requests()
    

    def build_single_spreadsheet(self, avg_faulting=False, 
                                 include_replaced=True,
                                 include_intensity_replaced=False):
        """Builds a single spreadsheet with all the registration data. The 
        single associating slab in the CY is the one that has the most overlap
        with the BY slab. If the avg_faulting flag is set to True, then all 
        CY slabs' faulting values that are associated with the BY slab will be
        averaged together instead of just using the CY slab with the majority 
        overlap.

        Args:
            avg_faulting (bool, optional): If True, the average faulting of the
            CY slabs will be calculated. Defaults to False.
        """
  
        self.reset_progress.emit()
        self.progress_max.emit(len(self.reg_data))  
            
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
            for year in self.years:
                fields.append(f'{year}_total_crack_length')
            for year in self.years:
                fields.append(f'{year}_average_crack_width')
            
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
                        # TODO: Add parameter to show annotated intensity images
                        if ('intensity_replaced' in yr_slab and (include_intensity_replaced 
                            and yr_slab['intensity_replaced'] == 'R')):
                            row_dict[f'{year}_state'] = 'R'
                        else:
                            row_dict[f'{year}_state'] = yr_slab['primary_state']

                        
                        # row_dict[f'{year}_state'] = yr_slab['primary_state'] if (
                        #     yr_slab['special_state'] != 'R' or not include_replaced) else (
                        #     yr_slab['special_state'])
                        row_dict[f'{year}_faulting'] = (
                            self.avg_faulting_BY(i, year) if avg_faulting
                            else yr_slab['mean_faulting']
                            )
                        row_dict[f'{year}_total_crack_length'] = yr_slab['total_crack_length'] if 'total_crack_length' in yr_slab else None
                        row_dict[f'{year}_average_crack_width'] = yr_slab['avg_crack_width'] if 'avg_crack_width' in yr_slab else None
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
                self.progress.emit(i + 1)
        

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


                    



    

