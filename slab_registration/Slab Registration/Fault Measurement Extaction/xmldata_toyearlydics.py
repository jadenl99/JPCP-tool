import pandas
from statistics import mean


csv_ready = False
excel_ready = False
yr = ""
while csv_ready == False:
    try:
        filename = input("Enter name of CSV file, make sure folder is saved in the same directory as this code (ex. 2015.csv):\n")
        csv_df = pandas.read_csv(filename, index_col = 0)
        csv_dict = csv_df.to_dict("index")
        csv_ready = True
    except: 
        continue
while excel_ready == False:
    try:
        filename = input("Enter name of Excel file, make sure folder is saved in the same directory as this code (ex. 2014_IRI_Fault_DataExtraction.xlsx):\n")
        yr = filename[0:4]
        xml_df = pandas.read_excel(filename, index_col = 0)
        xml_df = xml_df.fillna("")
        xml_dict = xml_df.to_dict("index")
        excel_ready = True
    except: 
        continue


# Creating Joint List
count = 1
joints_dict = {}
faults_dict = {}
for h in xml_dict:
    joints = []
    faults = []
    for i in xml_dict[h]:
        if i[0:5] == "Fault": 
            if(xml_dict[h][i] == ""):
                break
            faults.append(float(xml_dict[h][i]))
        elif i == "YAvg - Joint 1":
            if(xml_dict[h][i] == ""):
                break
            joints.append(float(xml_dict[h][i]))
        elif i[0:4] == "YAvg":
            if(xml_dict[h][i] == ""):
                break
            
            val_fault = faults.pop(-1)
            val = float(xml_dict[h][i])
            

            foundmatch = False
            for j in joints: 
                if abs(val-j) < 600:
                    foundmatch=True

                    ind = joints.index(j)
                    faluts_value_to_replace = faults[ind]
                    if faluts_value_to_replace == -10000 and val_fault != -10000:
                        faults.append(val_fault)
                    elif faluts_value_to_replace != -10000 and val_fault == -10000:
                        faults.append(faluts_value_to_replace)
                    else:
                        faults.append(round((faluts_value_to_replace + val_fault)/2.0, 2))
                    faults.remove(faluts_value_to_replace)

                    mn = (val+j)/2.0
                    joints.append(round(mn,2))
                    joints.remove(j)
                    break      
            if(foundmatch == False):
                joints.append(val)
                faults.append(val_fault)
            
    joints_dict[count] = joints
    faults_dict[count] = faults
    count += 1

# Creating XML file number list in CSV
slab = 1
filenum = 1
while slab <= len(csv_dict):
    if int(csv_dict[slab]["y_offset"]) <= (filenum * 5000):
        csv_dict[slab]["XML File Number"] = filenum
        slab += 1
    else: 
        filenum += 1

for i in csv_dict:
    joint_filenum = csv_dict[i]["XML File Number"]
    file_jointlist = joints_dict[joint_filenum]
    for j in file_jointlist:
        if abs(int(csv_dict[i]["y_offset"]) % 5000 - j) <= 500:
            ind = file_jointlist.index(j)
            if(j < 500):
                try:
                    j_plus_1 = joints_dict[joint_filenum - 1]
                    first_joint = min(j_plus_1)
                    if(first_joint > 4500 ):
                        ind2 = j_plus_1.index(first_joint)
                        val1 = faults_dict[joint_filenum][ind] 
                        val2 = faults_dict[joint_filenum - 1][ind2]
                        if val1 == -10000 and val2 != -10000:
                            csv_dict[i]["Fault Value"] = val2
                        elif val1 != -10000 and val2 == -10000:
                            csv_dict[i]["Fault Value"] = val1
                        else:
                            avg_fault = (val1 + val2)/2
                            csv_dict[i]["Fault Value"] = avg_fault
                    else:
                        csv_dict[i]["Fault Value"] = faults_dict[joint_filenum][ind]
                except:
                    csv_dict[i]["Fault Value"] = faults_dict[joint_filenum][ind]        
            else:
                csv_dict[i]["Fault Value"] = faults_dict[joint_filenum][ind]

#print(joints_dict)
#print(faults_dict)



# IRI
for i in csv_dict: 
    xml_num = csv_dict[i]["start_im"][13:19]
    try:
        csv_dict[i]["IRI Right"] = xml_dict[csv_dict[i][xml_num]]["IRI Right"]
        csv_dict[i]["IRI Left"] = xml_dict[csv_dict[i][xml_num]]["IRI Left"]
    except:
        continue


ret_df = pandas.DataFrame.from_dict(csv_dict, orient = "index")
ret_df.to_excel(yr + "slabdic_xml.xlsx", index = True)
print("Data successfully exported.")