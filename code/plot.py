import csv
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import matplotlib.patches as mpatches
import scipy.stats as st
import math

with open('latency_1robot.csv', 'r',encoding='unicode_escape')as latency1: 
    latency1=list(csv.reader(latency1))
    l1=[i[2] for i in latency1]
    s1=[i[3] for i in latency1]

with open('latency_2robot_machine1.csv', 'r',encoding='unicode_escape')as latency2: 
    latency2=list(csv.reader(latency2))
    l2=[i[2] for i in latency2]
    s2=[i[3] for i in latency2]

with open('latency_2robot_machine2.csv', 'r',encoding='unicode_escape')as latency3: 
    latency3=list(csv.reader(latency3))
    l3=[i[2] for i in latency3]
    s3=[i[3] for i in latency3]

with open('latency_3robot_machine1.csv', 'r',encoding='unicode_escape')as latency4: 
    latency4=list(csv.reader(latency4))
    l4=[i[2] for i in latency4]
    s4=[i[3] for i in latency4]

with open('latency_3robot_machine2.csv', 'r',encoding='unicode_escape')as latency5: 
    latency5=list(csv.reader(latency5))
    l5=[i[2] for i in latency5]
    s5=[i[3] for i in latency5]

with open('latency_3robot_machine3.csv', 'r',encoding='unicode_escape')as latency6: 
    latency6=list(csv.reader(latency6))
    l6=[i[2] for i in latency6]
    s6=[i[3] for i in latency6]


fig_width = 6.5
barwidth = 0.4
bardistance = barwidth * 1.7
colordict = {
            'compute_forward': '#0077BB',
            'store_forward': '#DDAA33',
            'store_forward_ia': '#009988',
            'orange': '#EE7733',
            'red': '#993C00',
            'blue': '#3340AD'}

markerdict = {
            'compute_forward': 'o',
            'store_forward': 'v',
            'store_forward_ia': 's'}

colorlist = ['#DDAA33', '#7ACFE5', '#3F9ABF',
            '#024B7A',  '#0077BB', '#009988']

markerlist = ['o', 'v', '^', '>', 'p', 's']

x = list(range(len(l6)))

s1 = list(map(int,s1))
s2 = list(map(int,s2))
s3 = list(map(int,s3))
s4 = list(map(int,s4))
s5 = list(map(int,s5))
s6 = list(map(int,s6))
l1 = [ 1000*float(x) for x in l1 ]
l2 = [ 1000*float(x) for x in l2 ]
l3 = [ 1000*float(x) for x in l3 ]
l4 = [ 1000*float(x) for x in l4 ]
l5 = [ 1000*float(x) for x in l5 ]
l6 = [ 1000*float(x) for x in l6 ]

t1 = [round(a / b ,3) for a, b in zip(s1, l1)] 
t2 = [round(a / b ,3) for a, b in zip(s2, l2)] 
t3 = [round(a / b ,3) for a, b in zip(s3, l3)] 
t4 = [round(a / b ,3) for a, b in zip(s4, l4)] 
t5 = [round(a / b ,3) for a, b in zip(s5, l5)] 
t6 = [round(a / b ,3) for a, b in zip(s6, l6)] 


"""
l1 = list(map(int,l1))
l2 = list(map(int,l2))
l3 = list(map(int,l3))
l4 = list(map(int,l4))
l5 = list(map(int,l5))
l6 = list(map(int,l6))

l1=np.array(l1)*0.001
l2=np.array(l2)*0.001
l3=np.array(l3)*0.001
l4=np.array(l4)*0.001
l5=np.array(l5)*0.001
l6=np.array(l6)*0.001
"""
x=np.array(x)
x=x*0.027

#l=np.array(numbers)*0.001


"""

#my_y_ticks = np.arange()
print(x,t6)
plt.scatter(x,t6,s=5)
plt.ylim(ymax=1400)
plt.ylim(ymin=400)

#plt.yticks(my_y_ticks)
plt.xlabel('time(s)')
plt.ylabel('Throughput(kBps)')
plt.show()

"""
box_2= plt.boxplot([t1,t2,t3,t4,t5,t6], positions=[1,2,3,4,5,6], vert=True, widths=barwidth, showfliers=False, showmeans=False, patch_artist=True,
                  boxprops=dict(
                      color='black', facecolor=colorlist[1], lw=1),
                  medianprops=dict(color='black'),
                  capprops=dict(color='black'),
                  whiskerprops=dict(color='black'),
                  flierprops=dict(
                      color=colorlist[1], markeredgecolor=colorlist[0], ms=4),
                  meanprops=dict(markerfacecolor='black', markeredgecolor='black'))
#plt.title("Total energy")
plt.ylim(ymax=4000)
plt.ylim(ymin=0)
plt.xlabel("Number of slaver robots")
plt.ylabel("Throughput(kBps)")



plt.show()
