import numpy as np
import random

from plot import *
from pop import Population
from traf import Traffic

import matplotlib.pylab as plt

def rand_des():
    rand=random.random()
    p_all=0
    for i in range(50):
        p_all+=p[i]
    p_now=0
    for i in range(50):
        if rand<(p[i]+p_now)/p_all:
            return i
        p_now+=p[i]
    return 49

def distance(x,y):
    ab=np.abs(x-y)
    return ab[0]+ab[1]

trafPath = "data/over.xlsx"
popPath = "img/pop_den_trace.jpg"

longitudeRange = [120.85, 121.98]
latitudeRange = [30.67, 31.51]

traf = Traffic(trafPath)
pop = Population(popPath, longitudeRange, latitudeRange)

sheet=get_sheet()

#get des_p , des_in_which_route
des_in_which_route= [0 for i in range(50)]
p=[0 for i in range(50)]
num_=0
for i in range(6):
    bo=0
    for j in sheet[i].values:
        if bo==0:
            bo=1
        else:
            trafDen = traf.estimateDensity([j[0], j[1]], 8e-3) / 350
            popDen = pop.estimateDensity([j[0], j[1]]) / 4.8e4
            den = trafDen * popDen
            if den != 0:
                den /= (trafDen + popDen)
            p[num_]= den
            des_in_which_route[num_]=i
            num_+=1

#get route_time
route_time=[0 for i in range(6)]
d=[0 for i in range(50)]
max_routetime=60
num_=0
for i in range(6):
    bo=0
    for j in sheet[i].values:
        if bo==0:
            bo=1
            last=j
        else:
            route_time[i]+=distance(j,last)
            d[num_]=route_time[i]
            num_+=1
            last=j

route_time=np.array(route_time)
route_time=np.array(route_time * max_routetime / np.max(route_time),dtype=np.int16)

d=np.array(d)
price=np.array(d * 20/ np.max(d),dtype=np.int16)

print(price)

np.random.seed(0)
num = np.random.normal(90,20,18000)
num = np.array(num,dtype=np.int16)
num = sorted(num)
des = []
for i in range(18000):
    des.append(rand_des())
des = np.array(des)

s = np.vstack((num,des,np.array(range(18000)))).T
time_des=[[] for i in range(180)]
for array_ in s:
    time_des[array_[0]].append((array_[1],array_[2],array_[0]))


num_time=[0 for i in range(180)]
for i in range(180):
    num_time[i]=len(time_des[i])



taxi_p = 1.0*7000/18000 
bus_p = taxi_p+ 1.0*1200/18000 
wait = 1-bus_p

#s[no]: arrival time,  destination, no.
#time_des[time]: des, no, time

def get_wait_time(car_n):
    car_time=np.ones(180) * car_n
    when_to_go=np.zeros(18000)
    seats=33

    count_n=[[] for i in range(6)]
    last_n=[[] for i in range(6)]

    for time_ in time_des:
        lst=[]
        for (i, person, time__) in time_:
            rand=random.random()
            if rand<taxi_p:
                when_to_go[person]=-1
                continue
            elif rand<bus_p:
                when_to_go[person]=-2
                continue
            count_n[des_in_which_route[i]].append(person)
            if len(count_n[des_in_which_route[i]])+len(last_n[des_in_which_route[i]])>=seats:
                add=[]
                price_ = 0
                for k in range(seats):
                    if len(last_n[des_in_which_route[i]]) != 0:
                        pop_=last_n[des_in_which_route[i]].pop()
                        add.append(pop_)
                        price_+=price[s[pop_][1]]
                    else:
                        pop_=count_n[des_in_which_route[i]].pop()
                        add.append(pop_)
                        price_+=price[s[pop_][1]]
                lst.append([price_,des_in_which_route[i],add])

        lst.sort(reverse=True)
        for pair in lst:
            if car_time[time_[0][2]]>0:
                for i in range(180):
                    if i>=time_[0][2]:
                        car_time[i] -= 1
                for i in range(180):
                    if i>=time_[0][2]+route_time[pair[1]]:
                        car_time[i]+=1
                for item in pair[2]:
                    when_to_go[item]=time_[0][2]
            else:
                last_n[pair[1]]+=pair[2]
        for i in range(6):
            last_n[i]=last_n[i]+count_n[i]
            count_n[i]=[]
    wait_time=[]
    car_and_bus=0
    average_living_time=[]
    for i in range(18000):
        if when_to_go[i]>0:
            wait_time.append([s[i][0],when_to_go[i]-s[i][0]])
            average_living_time.append(when_to_go[i]-s[i][0])
        elif when_to_go[i] !=0 and when_to_go[i]!=-3:
            car_and_bus+=1
    print('taxi_and_bus=', car_and_bus)
    wait_time=np.array(wait_time)
    print('carry_how_many_people=',wait_time.shape[0])
    average_living_time=np.array(average_living_time)
    print('average_living_time=', average_living_time.mean())
    return wait_time

car_n_=[100,150,200]
for car_n in car_n_:
    wait_time=get_wait_time(car_n)
    plt.scatter(wait_time[:,0],wait_time[:,1],s=1,marker='s')
plt.xlim([0,180])
plt.xlabel('Time T (m)')
plt.ylabel('Wait Time (m)')
plt.legend(('100','150','200'))
plt.show()

