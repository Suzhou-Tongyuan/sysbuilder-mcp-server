import numpy as np
import matplotlib.pyplot as plt
import random

#支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']

#雷达图
#values数组是雷达图各轴需要显示的实例对象的各属性
values = [车A.成本/1000,车A.质量*100,车A.最大速度,车A.电池容量]
values2 = [车B.成本/1000,车B.质量*100,车B.最大速度,车B.电池容量]
values3 = [车C.成本/1000,车C.质量*100,车C.最大速度,车C.电池容量]
values4 = [车D.成本/1000,车D.质量*100,车D.最大速度,车D.电池容量]
#feature数组是雷达图各轴的标题文字
feature = ['成本','质量','最大速度','电池容量']

N = len(values)
angles=np.linspace(0, 2*np.pi, N, endpoint=False)

#将以下数组拼接成环形
values=np.concatenate((values,[values[0]]))
values2=np.concatenate((values2,[values2[0]]))
values3=np.concatenate((values3,[values3[0]]))
values4=np.concatenate((values4,[values4[0]]))

angles=np.concatenate((angles,[angles[0]]))
feature=np.concatenate((feature,[feature[0]]))

fig=plt.figure(figsize=(10,5))
fig.subplots_adjust(wspace=0.4)

#画布被分为一行两列，雷达图在第一列
ax1 = fig.add_subplot(1,2,1, polar=True)

#雷达图各轴的属性值和标签
ax1.plot(angles, values, 'o-', linewidth=2, label = 'A')
ax1.fill(angles, values, alpha=0.25)
ax1.plot(angles, values2, 'o-', linewidth=2, label = 'B')
ax1.fill(angles, values2, alpha=0.25)
ax1.plot(angles, values3, 'o-', linewidth=2, label = 'C')
ax1.fill(angles, values3, alpha=0.25)
ax1.plot(angles, values4, 'o-', linewidth=2, label = 'D')
ax1.fill(angles, values4, alpha=0.25)


ax1.set_thetagrids(angles*180/np.pi, feature)
ax1.set_ylim(auto = True)
plt.title('各属性对比雷达图')
ax1.grid(True)
plt.legend(loc = 'best')

#条形图
#画布被分为一行两列，条形图在第二列
ax2 = fig.add_subplot(1,2,2)

#x轴显示文字
lstX = []
lstX.append('A')
lstX.append('B')
lstX.append('C')
lstX.append('D')

#y轴显示值
aValue = 车A.电池容量 * 车A.最大速度  / (车A.成本 )
bValue = 车B.电池容量 * 车B.最大速度 / (车B.成本 )
cValue = 车C.电池容量 * 车C.最大速度  / (车C.成本 )
dValue = 车D.电池容量 * 车D.最大速度  / (车D.成本 )


lstY = []
lstY.append(aValue)
lstY.append(bValue)
lstY.append(cValue)
lstY.append(dValue)

#颜色和标题文字
plt.bar(lstX, lstY, 0.6, color='#87CEFA')
plt.xlabel('车辆设计方案')                         
plt.ylabel('性价比') 
plt.title('性价比条形图') 

plt.show()

