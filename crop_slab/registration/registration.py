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
                str(self.by): [x['_id']]
            } 
            for x in self.by_slabs
            ]
        print("Running code...")
        self.register()
        print(self.reg_data)
       

        
    def register(self):
        for year, first_slab in zip(self.years, self.first_slabs):
            self.align_year(year, first_slab)
            if year != self.by: 
                self.categorize(year, first_slab)



    def prompt_input(self):
        while self.years == None:
            years_input = input("Enter years from least to greatest, separate them with a comma (ex. 2014, 2015, 2017):\n").split(", ")
            try: 
                self.years = [int(x) for x in years_input]
            except:
                None
        
        while self.by not in self.years:
            try:
                self.by = int(input("Enter base year, this should be a year within the list inputed previously:\n"))
            except:
                None
        
        while self.first_slabs == None or len(self.first_slabs) != len(self.years):
            first_slabs_input = input("Enter the first slab index for each year to align by, separate them with a comma (ex. 1, 3, 5):\n").split(", ")
            try:
                self.first_slabs = [int(x) for x in first_slabs_input]
            except:
                None


    def align_year(self, year: int, first_slab: int):
        slab_data = self.writer.get_slab_data(year, first_slab)
        shift = -(slab_data['y_offset'])
        self.writer.update_offsets(year, shift)


    def categorize(self, year: int, first_slab: int):
        # list of current slabs
        cy_slabs = list(self.writer.get_year_slab_data(year, first_slab))
        self.reg_data[0][str(year)] = []   
        cy_entries = self.reg_data[0][str(year)]
        byi, cyi = 0, 0
        while byi < len(self.by_slabs) and cyi < len(cy_slabs):
            # WARNINGS
            if byi >= len(self.by_slabs) + 1:
                raise Exception(f"Stopped when processing slab "
                                f"{cy_slabs[cyi]['slab_index']} of year "
                                f"{year}. Summation on total slab lengths "
                                f"between {self.by} and {year} do not match."
                                )
            # TODO: account for other error?
            by_length = self.by_slabs[byi]['length']
            cy_length = cy_slabs[cyi]['length']
            by_offset = self.by_slabs[byi]['y_offset']
            cy_offset = cy_slabs[cyi]['y_offset']
            overlap_type = overlap.belongs_to(by_offset, by_length, cy_offset, cy_length)
            if overlap_type == OverlapType.FULL_OVERLAP:
                cy_entries.append(cy_slabs[cyi]['_id'])
            elif overlap_type == (OverlapType.BASE_MAJORITY_OVERLAP or 
                                  OverlapType.CURRENT_MAJORITY_OVERLAP):
                cy_entries.append(cy_slabs[cyi]['_id'])
                if self.reg_data[byi]["replaced"] == None:
                    self.reg_data[byi]["replaced"] = year

            if by_offset < cy_offset:
                byi += 1
                if byi < len(self.by_slabs):
                    self.reg_data[byi][str(year)] = []
                    cy_entries = self.reg_data[byi][str(year)]
            else:
                cyi += 1
    
    
    # def register(self, year, slab_obj_id, byi):
    #     """Registers the slab object to the base year slab

    #     Args:
    #         year (int): year of the slab object
    #         slab_obj_id (int): slab object ID
    #         byi (int): index of the base year slab
    #     """
    #     if str(year) not in self.reg_data[byi]:
    #         self.reg_data[byi][str(year)] = []

    #     self.reg_data[byi][str(year)].append(slab_obj_id)
       
