# judge.py

import numpy as np

length = 231
width = 94
height = 94

def packing3d(B):
    _list = [(0,0,0)]
    lx = 0
    lz = 0

    #sort(B)
    E=np.zeros((length,width,height))
    def sum_(x,y,z,v):
        _sum_ = 0
        for ii in range(v[0]):
            for jj in range(v[1]):
                for kk in range(v[2]):
                    _sum_+=E[x+ii][y+jj][z+kk]
        return _sum_

    def packinv(x,y,z,v):
        if x+ v[0]<= length and y+v[1]<=width and z+v[2]<=height:
            if sum_(x,y,z,v)==0:
                return True
        return False

    def sort_(_list):
        for i in range(len(_list)):
            for j in range(len(_list)):
                if i<j:
                    if _list[i][0]<_list[j][0] or (_list[i][0]==_list[j][0] and _list[i][1]<_list[j][1]) or (_list[i][0]==_list[j][0] and _list[i][1]==_list[j][1] and _list[i][2]<_list[j][2]):
                        t=_list[i]
                        _list[i]=_list[j]
                        _list[j]=t
        return _list
    #sorted(B,lambda x: x.volume())
    num=0
    success =0 
    while num<len(B):
        v= B[num]
        #print('*******num=*******',num)
        #print('v=',v)
        flag = False
        for item in _list:
            #print(_list)
            x=item[0]
            y=item[1]
            z=item[2]
            #print('101=',packinv(1,0,1,v))
            if x+ v[0]<= lx and z+v[2]<=lz and packinv(x,y,z,v):
                flag = True
                break
        if flag == False:
            if lx==0 or lx == length:
                if packinv(0,0,lz,v):
                    x=0
                    y=0
                    z=lz
                    flag = True
                    lz= lz+ v[2]
                    lx= v[0]
                    #print(lx,lz)
                elif lz<height:
                    lz=height
                    lx=length
                    num-=1
            else:
                for item in _list:
                    x=item[0]
                    y=item[1]
                    z=item[2]
                    if x==lx and y==0 :
                        if packinv(x,y,z,v) and z+v[2]<=lz:
                            flag = True
                            lx=lx+v[0]
                            break
                if flag == False:
                    lx=length
                    num-=1
        if flag == True:
            for i in range(len(_list)):
                if _list[i]==(x,y,z):
                    _list.pop(i)
                    break
            #print(x,y,z)
            while x>0:
                if sum_(x-1,y,z,v)==0:
                    x-=1
                else:
                    break
            while y>0:
                if sum_(x,y-1,z,v)==0:
                    y-=1
                else:
                    break
            while z>0:
                if sum_(x,y,z-1,v)==0:
                    z-=1
                else:
                    break
            #print('xyz=',x,y,z)
            for ii in range(v[0]):
                for jj in range(v[1]):
                    for kk in range(v[2]):
                        #print(x+ii,y+jj,z+kk,num+1)
                        E[x+ii][y+jj][z+kk]=num+1
            _list.append((x+v[0],y,z))
            _list.append((x,y+v[1],z))
            _list.append((x,y,z+v[2]))
            _list = sort_(_list)
            #print(_list)
            success +=1
        num+=1
    return success == len(B)

