import pandas
import copy
import sys, os
from os.path import exists

class SlabRegistration:
    def __init__(self):

        self.application_path = ""
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        elif __file__:
            self.application_path = os.path.dirname(__file__)

        self.year_dics = {}
        self.master = {}
        self.by_dic = {}
        self.minslablength = 100
        self.possiblyor = 2
        self.states = ["", "NAN", "BRIDGE", "NC", "L1", "T1", "L2", "T2", "CC", "SS"]  

        #TEMP
        #self.fault_measurements_path = "XMLFiles_Averages.xlsx"  

        self.years = None
        while self.years == None:
            years_input = input("Enter years from least to greatest, separate them with a comma (ex. 2014, 2015, 2017):\n").split(", ")
            try: 
                self.years = [int(x) for x in years_input]
            except:
                None
        
        self.by = None
        while self.by not in self.years:
            try:
                self.by = int(input("Enter base year, this should be a year within the list inputed previously:\n"))
            except:
                None

        self.interstate = input("Enter interstate name (ex. I-20):\n")
        self.interval = 4
        directions = ["NB", "SB", "WB", "EB"]
        self.direction = None
        while self.direction not in directions:
            try:
                self.direction = input("Enter interstate direction (either NB or SB or WB or EB):\n")
            except:
                None

        self.mp = None
        while isinstance(self.mp, int) == False :
            try:
                self.mp = int(input("Enter starting milepost (ex. 22):\n"))
            except:
                None
        
        self.data_filepath = "notafile.txt"
        while exists(self.data_filepath) == False :
            try:
                inputfilepath = input("Enter the name of your datafile, make sure it is saved in the same directoy as where you are running this code (ex. data.xlsx):\n")
                self.data_filepath = self.application_path + "/" + inputfilepath
            except:
                None

        print("Running code...")
        self.out_filepath = self.interstate + "_MP" + str(self.mp) + "_BY" + str(self.by) + "_SlabRegistrationOutput.xlsx"
        self.app_filepath = self.interstate + "_MP" + str(self.mp) + "_BY" + str(self.by) + "_SlabClassificationInput.xlsx"
        self.fault_filepath = self.interstate + "_MP" + str(self.mp) + "_BY" + str(self.by) + "_Faulting.xlsx"
        

        self.build(self.data_filepath, self.out_filepath)

       

    def prepare_data(self, filepath):
        for y in self.years:
            y_df = pandas.read_excel(filepath, sheet_name = str(y), dtype = {"slab_index": int})
            y_df["Length"] = y_df["Length"]/304.8
            if "Slab State" not in y_df.columns:
                y_df["Slab State"] = ""
            if "Slab State 2" not in y_df.columns:
                y_df["Slab State 2"] = ""
            if "Fault Value" not in y_df.columns:
                y_df["Fault Value"] = ""
                self.run_fault = False
            else: 
                self.run_fault = True
            
            y_df.index = y_df.index + 1 # have indexes start at 1
            y_df = y_df.round({'Length': 2})
            y_df["Slab State"] = y_df["Slab State"].fillna("NAN")
            y_df["Slab State"] = y_df["Slab State"].replace([0], "NC")
            y_df = y_df.rename(columns = {"slab_index": "Slab ID"})
            y_df['Matching Slab ID'], y_df['Within Slabs'], y_df['Replaced'], y_df['Possibly OR'], y_df['Matching Slab Index'] = ["", "", "", "", ""]

            self.minslablength = min(self.minslablength, y_df["Length"].min())
            if (self.interval >= self.minslablength):
                raise Exception("Interval is greater than smallest slab. Please fix data.")

            #Fault Measuements being excluded below
            y_dic = y_df[["Slab ID", "Length", "Slab State", "Slab State 2", "Matching Slab ID", "Matching Slab Index", "Within Slabs", "Replaced", "Possibly OR", "start_im", "end_im", "Fault Value"]].to_dict("index")
            self.year_dics[y] = y_dic
        
        self.by_dic = self.year_dics[self.by]



    def setup_master(self):
        numslabs = list(self.year_dics[self.by].keys())[-1]
        
        master_columns = self.years + ["Replaced", "Year Replaced", "Replaced and Broken"]
        master_columns.remove(self.by)

        for n in range(1, numslabs + 1): # Building rows of the data frame (each is a dictionaty corresponding to one slab that lives inside a master dictionary)
            temp = {}
            
            temp["Interstate"] = self.interstate
            temp["Direction"] = self.direction
            temp["Slab ID"] = self.by_dic[n]["Slab ID"]
            temp["BY Length (ft)"] = self.by_dic[n]["Length"]
            temp[self.by] = self.by_dic[n]["Slab State"]
            
            if n == 1:
                temp["MP From"] = self.mp
            else: 
                temp["MP From"] = round(self.master[n-1]["MP To"],4)

            if self.direction == "WB" or self.direction == "SB":
                temp["MP To"] =  round(temp["MP From"] - self.by_dic[n]["Length"]/5280,4)
            else:
                temp["MP To"] =  round(temp["MP From"] + self.by_dic[n]["Length"]/5280,4)
            
            if self.by_dic[n]["Length"] <= self.possiblyor:
                temp["Possibly OR"] = 1
            else: 
                temp["Possibly OR"] = None
            

            for y in master_columns:
                temp[y] = None
                self.master[n] = temp
                        
    def categorize(self, year):
        length = 0
        carryover = 0

        by_slabindex = 1

        cy_dic = self.year_dics[year]

        for n in self.year_dics[year]:
            
            #WARNINGS
            if by_slabindex >= len(self.by_dic) + 1:
                raise Exception("STOPED when proccessing slab " + str(cy_dic[n]["Slab ID"]) + " of year " + str(year) + ". Summation on total slab lengths between " + str(self.by) + " and " + str(year) + " do not match.")

            if ((cy_dic[n]["Length"]) > 40) and (cy_dic[n]["Length"] > (self.by_dic[by_slabindex]["Length"] + self.interval)):
                print("Possible error in slab length for Slab ID " + str(n) + " of year " + str(year) + "." )

           
            # Slab Replacement Within Original Slab Limits

            if cy_dic[n]["Length"]  <= (self.by_dic[by_slabindex]["Length"] - length) + self.interval:
                cy_dic[n]["Matching Slab ID"] = self.by_dic[by_slabindex]["Slab ID"]
                cy_dic[n]["Matching Slab Index"] = by_slabindex
                length = length + cy_dic[n]["Length"]

                # Stats
                if cy_dic[n]["Length"] + self.interval < self.by_dic[by_slabindex]["Length"]:
                    cy_dic[n]["Replaced"] = year
            
            # Replacing the common joint location (creating a new small slab)

            elif cy_dic[n]["Length"] > (self.by_dic[by_slabindex]["Length"] - length):
                
                if (self.by_dic[by_slabindex]["Length"] - length) >= (cy_dic[n]["Length"]/2.0):
                    cy_dic[n]["Matching Slab ID"] = self.by_dic[by_slabindex]["Slab ID"]
                    cy_dic[n]["Matching Slab Index"] = by_slabindex
                    #Stats
                    cy_dic[n]["Within Slabs"] = str(self.by_dic[by_slabindex]["Slab ID"]) + ", " + str(self.by_dic[by_slabindex]["Slab ID"] + 1)
                    #Update parameters
                    carryover = cy_dic[n]["Length"] - (self.by_dic[by_slabindex]["Length"] - length)
                    length = length + cy_dic[n]["Length"] - carryover
                else:
                    cy_dic[n]["Matching Slab ID"] = self.by_dic[by_slabindex]["Slab ID"] + 1
                    cy_dic[n]["Matching Slab Index"] = by_slabindex + 1
                    #Stats
                    cy_dic[n]["Within Slabs"] = str(self.by_dic[by_slabindex]["Slab ID"]) + ", " + str(self.by_dic[by_slabindex]["Slab ID"] + 1)
                    #Update parameters
                    carryover = cy_dic[n]["Length"] - (self.by_dic[by_slabindex]["Length"] - length)
                    length = length + cy_dic[n]["Length"] - carryover

                #Stats
                cy_dic[n]["Replaced"] = year

            if length >= self.by_dic[by_slabindex]["Length"] - self.interval:
                
                #Replacing Original Slab with a Longer One

                if (by_slabindex < len(self.by_dic)) and (carryover + self.interval >= self.by_dic[by_slabindex + 1]["Length"]):
                    #Stats
                    cy_dic[n]["Replaced"] = year

                    cummulativelength = self.by_dic[by_slabindex + 1]["Length"]
                    for m in range(1, 10):
                        if carryover <= cummulativelength + self.interval:
                            length = max(carryover - cummulativelength, 0)
                            carryover = 0
                            by_slabindex = by_slabindex + 1 + m
                            break
                        else:
                            cummulativelength = cummulativelength + self.by_dic[by_slabindex + 1 + m]["Length"]
                else:
                    #Update paramteres
                    length = carryover
                    carryover = 0
                    by_slabindex = by_slabindex + 1
    
    def to_master(self):
        years_tm = copy.deepcopy(self.years)
        years_tm.remove(self.by)

        for ytemp in years_tm:
            y = self.year_dics[ytemp]
            for n in range(1, len(y) + 1):
                by_slab = y[n]["Matching Slab Index"]

                if self.master[by_slab][ytemp] == None:
                    self.master[by_slab][ytemp] = y[n]["Slab State"]
                else:
                    try: #CHECK THIS IS WORKING
                        self.master[by_slab][ytemp] = max(self.master[by_slab][ytemp], y[n]["Slab State"], key = lambda s : self.states.index(s))
                    except: 
                        self.master[by_slab][ytemp] = y[n]["Slab State"]
                
                if isinstance(y[n]["Replaced"],(int)):
                    self.master[by_slab]["Replaced"] = 1
                    if self.master[by_slab]["Year Replaced"] != None:
                        self.master[by_slab]["Year Replaced"] = min(self.master[by_slab]["Year Replaced"], y[n]["Replaced"])
                    else: 
                        self.master[by_slab]["Year Replaced"] =  y[n]["Replaced"]

                previousstate = None
                try: 
                    previousstate = self.master[by_slab][ytemp-1]
                except:
                    pass
                if (previousstate != None and previousstate in self.states):
                    if (self.states.index(previousstate) > self.states.index(y[n]["Slab State"]) ):
                        self.master[by_slab]["Replaced and Broken"] = 1
                
    def fault_across_years(self):
        fault_dic = {}

        for ytemp in self.years:
            fault_dic[ytemp] = {} 
            y = self.year_dics[ytemp]
            for n in range(1, len(y) + 1):
                if ytemp == self.by: 
                    by_slab = n
                else:    
                    by_slab = y[n]["Matching Slab Index"]
                
                fault_dic[ytemp][by_slab] = y[n]["Fault Value"]

        ret_df = pandas.DataFrame.from_dict(fault_dic, orient = "index")
        ret_df = ret_df.T
        ret_df = ret_df.sort_index()
        ret_df.to_excel(self.application_path + "/" + self.fault_filepath, index = True)


    def to_excel(self, filename):
        ret_df = pandas.DataFrame.from_dict(self.master, orient = "index")
        
        ex_columns = ["Interstate", "Direction", "MP From", "MP To", "Slab ID", "BY Length (ft)"] + self.years + ["Replaced", "Year Replaced", "Replaced and Broken", "Possibly OR"]
        ret_df = ret_df[ex_columns]
        ret_df = ret_df.rename(columns={"Slab ID": str(self.by) + " Slab ID"})

        ret_df.to_excel(self.application_path + "/" + filename, index = False)
        

    def build(self, data, out):
        self.prepare_data(data)
        self.setup_master()

        years_temp = copy.deepcopy(self.years)
        years_temp.remove(self.by)
        
        for y in years_temp:
            self.categorize(y)
        
        self.to_master()
        self.to_excel(out)
        self.for_categorization()

        if self.run_fault != False:
            self.fault_across_years()
    
    def for_categorization(self):
        writer = pandas.ExcelWriter(self.application_path + "/" + self.app_filepath)
        for y in self.years:
            y_df = pandas.DataFrame.from_dict(self.year_dics[y], orient='index')
            y_df["Comments"] = ""
            y_df.to_excel(writer, sheet_name = str(y), index_label = str(y) + " Slab ID")
        writer._save()
        writer.close()
        print("Data successfully exported.")
    
    # def fault_measurements(self):
    #     fm_df = pandas.read_excel(self.application_path + "/" + self.fault_measurements_path, index_col = 0)
    #     fm_dic = fm_df.to_dict("index")

    #     for y in self.years:
    #         year_dic = self.year_dics[y]
    #         for s in year_dic: 
    #             if int(year_dic[s]["start_im"][13:19]) in fm_dic:
    #                 year_dic[s]["Fault Measurement"] = fm_dic[str(y) + "-" + str(year_dic[s]["start_im"][13:19])]["Average 1"]


x = SlabRegistration()
