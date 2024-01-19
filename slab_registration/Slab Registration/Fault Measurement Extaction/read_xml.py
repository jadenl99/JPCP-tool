import pandas
import os
from bs4 import BeautifulSoup
from statistics import mean

data_ready = False
while data_ready == False:
    try:
        path = input("Enter name of folder with your XML files, make sure folder is saved in the same directory as this code (ex. XMLFiles):\n")
        dir_list = os.listdir(path)
        data_ready = True
    except: 
        continue
year = input("Enter year data corresponds to (ex. 2014):\n")

master = {}


try:
    dir_list.remove(".DS_Store")
except: 
    None

xml_list = os.listdir(path)
for x in xml_list:
    if(str(x)[0:4] != "Lcms"):
        continue

    str_x = str(x)[11:17]
    if(str_x != "" and int(str_x)%100 == 0):
        print(100)
    
    master[str_x] = {}
    master[str_x]["Year"] = year
    
    with open(path + "/" + x, 'r') as f:
        data = f.read()

    xml_data = BeautifulSoup(data, "xml")

    tags_list = xml_data.find_all('Joint')
    iri_list = xml_data.find_all("IRI")

    if(iri_list != None):
        try:
            iri_left_raw = iri_list[1].getText().split(" ")
            iri_left = [float(i) for i in iri_left_raw if i != ""]
            master[str_x]["IRI Left"] = round(mean(iri_left), 2)

            iri_right_raw = iri_list[2].getText().split(" ")
            iri_right = [float(i) for i in iri_right_raw if i != ""]
            master[str_x]["IRI Right"] = round(mean(iri_right), 2)
            #master[str(y) + "-" + str(x[:-4])]["IRI Average"] = round((mean(iri_left)+mean(iri_right))/2, 2)
        except:
            None
    
    if(len(tags_list) > 0):
        for i in range(0, len(tags_list)): 
            fault = tags_list[i].find("FaultMeasurements")
            if(fault != None):
                fault_text = fault.getText().split(" ")
                measurement_list_clean = [float(i) for i in fault_text if i != "-10000.0"]

                try:
                    master[str_x]["Fault - Joint " + str(i + 1)] = round(mean(measurement_list_clean), 2)
                except:
                    master[str_x]["Fault - Joint " + str(i + 1)] = 0
                
                y1 = float(tags_list[i].find("Y1").getText())
                y2 = float(tags_list[i].find("Y2").getText())
                ylist = [y1, y2]
                yavg = mean(ylist)

                master[str_x]["Y1 - Joint " + str(i + 1)] = y1
                master[str_x]["Y2 - Joint " + str(i + 1)] = y2
                master[str_x]["YAvg - Joint " + str(i + 1)] = yavg



ret_df = pandas.DataFrame.from_dict(master, orient = "index")
ret_df = ret_df.sort_index()
ret_df.to_excel(path + "_IRI_Fault_DataExtraction.xlsx", index = True)
print("Data successfully exported.")


