import csv
from locale import ABDAY_1
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time


def get_index1(lst=None, item=''):
    tmp = []
    tag = 0
    for i in lst:
        if i == item:
            tmp.append(tag)
        tag += 1
    return tmp



with open('master_3robot_t.csv', 'r',encoding='unicode_escape')as master: 
    next(master)
    data_m = csv.reader(master)
    data_m = list(data_m)
    number_m = [i[0] for i in data_m] 
    time_m = [i[1][:-3] for i in data_m] 
    src_m = [i[2] for i in data_m] 
    dst_m = [i[3] for i in data_m] 
    Prot_m = [i[4] for i in data_m] 
    id_m= [i[5] for i in data_m] 
    size_m = [i[6] for i in data_m]
    time_m_delta = [i[7] for i in data_m] 
    #print(time_m[10])
   # print(data_m.shape)

with open('slaver_3robot_machine3_t.csv', 'r',encoding='utf-8')as slaver: 
    next(slaver)
    data_s = list(csv.reader(slaver))
    number_s = [i[0] for i in data_s] 
    time_s = [i[1][:-3] for i in data_s] 
    src_s = [i[2] for i in data_s] 
    dst_s = [i[3] for i in data_s] 
    Prot_s = [i[4] for i in data_s] 
    id_s= [i[5] for i in data_s] 
    time_s_delta = [i[7] for i in data_s] 
    #print(time_s[1])

with open('master_3robot.csv', 'r',encoding='utf-8')as d1: 
    d1 = list(csv.reader(d1))
    idm= [i[0] for i in d1] 
    dm = [i[1] for i in d1]
    #print(dm)


with open('slaver_3robot_machine3.csv', 'r',encoding='utf-8')as d2: 
    d2 = list(csv.reader(d2))
    ids= [i[0] for i in d2] 
    ds = [i[1] for i in d2]
a = 0
w = 0
l = 0
nf = 0
wi=0
for i in range(1,len(data_m)) :
    if Prot_m[i] != "UDP" : 
        continue

    if src_m[i] != "192.168.2.10": 
        continue

    if dst_m[i] != "192.168.2.8":
        continue

    if id_m[i] in id_s :
        try:
            a=get_index1(idm,id_m[i])
            b=get_index1(ids,id_m[i])
            #print(a,b)
        except:
            print("nf:",i)
            nf +=1
            continue
        if len(a)==len(b)==1:

            if dm[a[0]]== ds[b[0]]:
                j=id_s.index(id_m[i])
                mt = datetime.datetime.strptime(time_m[i], "%Y-%m-%d %H:%M:%S,%f")
                st = datetime.datetime.strptime(time_s[j], "%Y-%m-%d %H:%M:%S,%f")
                latency = (mt-st)
        
                #print(i)
                #print(mt)
                #print(st)
                #print (latency)
                
                f = open('latency_3robot_machine3.csv', 'a')  # the file name
                f.writelines(str(mt))
                f.writelines(',')
                f.writelines(str(st))
                f.writelines(',')
                f.writelines(str(latency))
                f.writelines(',')
                f.writelines(str(size_m[i]))
                f.writelines('\n')
                f.close()
                continue
                
            else:
            
            
                w +=1
                print("l:",i,id_m[i])
                print(a,b)
                continue
        else:
            wi +=1
            continue
    else:
        l +=1
        continue



        
            
    


print("Data_number:",i)  
print("Wrong_packets:",w)
print("Packet_loss:",l)
print("Wrong_identification:",wi)
print("No_data:",nf)

        





""" 

      
       
    else:
        print(i)
        l +=1
    

print(l)
""" 