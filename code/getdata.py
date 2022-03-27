from scapy.all import *
import csv
pkts = rdpcap("master_3robot.pcapng")
k=0
for i in range(1,len(pkts)): 

    pkt0 = pkts[i]
    try:
        data = pkt0['Raw'].load
        id = pkt0['IP'].id
    except:
        k=k+1
        continue

   # print(hex(id))
        
    f = open('master_3robot.csv', 'a')  # the file name
    f.writelines('"')
    f.writelines('0x{:04x}'.format(id))
    f.writelines(' (')
    f.writelines(str(id))
    f.writelines(')"')
    f.writelines(',')
    f.writelines('"')
    f.writelines(str(data))
    f.writelines('"')
    f.writelines('\n')
    f.close()

print(k)