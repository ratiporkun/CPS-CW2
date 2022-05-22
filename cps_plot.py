# -*- coding: utf-8 -*-
"""cps_plot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-RrlXinmOVZCuIWCDQPQ7IYKclqBER07
"""

!pip install pulp

from google.colab import drive
import pandas as pd
from pulp import LpMinimize, LpVariable, lpSum, LpProblem
import matplotlib.pyplot as plt
import numpy as np
drive.mount('/content/drive')

f = pd.read_excel('/content/drive/My Drive/COMP3217CW2Input.xlsx', sheet_name = 'User & Task ID') # read the excel sheet 'User & Task ID'

f2 = pd.read_excel('/content/drive/My Drive/COMP3217CW2Input.xlsx', sheet_name = 'AbnormalGuidelinePricing') # read the excel sheet 'AbnormalGuidelinePricing'

#Convert columns to lists and store them in variables
users = f['User & Task ID'].tolist() 
ready_time = f['Ready Time'].tolist() 
deadline = f['Deadline'].tolist()
max = f['Maximum scheduled energy per hour'].tolist() 
energy_demand = f['Energy Demand'].tolist()

unit_cost = f2['Unit Cost'].tolist()

user_tasks = [] #array for each user/task combination
task_info = [] #array for information on each user/task combination 

for i in range(len(users)):
  tmp = []
  user_tasks.append(users[i])
  tmp.append(ready_time[i])
  tmp.append(deadline[i])
  tmp.append(max[i])
  tmp.append(energy_demand[i])
  task_info.append(tmp)

test_data = pd.read_csv('/content/drive/My Drive/test_data_labelled.txt', header = None)

y_test = test_data[24].tolist()
x_test = test_data.drop(24,axis=1).values.tolist()

# since the time slot of a specific user/task combination is deadline - ready time, I created an lp variable for each
# of the time slot for a given combination. For instance user1_task1 has deadline 23 and ready time 20 the lp variables for it
# will be user1_task1_20, user1_task1_21, user1_task1_22, user1_task1_23

def model_maker(user_tasks_p,task_info_p):

  lp_vars = []
  price_const = []
  model_f = LpProblem(name='energy_scheduling', sense=LpMinimize)
  for j in range(len(task_info_p)):
    tmp = []
    for k in range(task_info_p[j][0], task_info_p[j][1] + 1):
      lp_var = LpVariable(name=user_tasks_p[j] + '_' + str(k), lowBound=0, upBound=1) # give lowBound as 0 since deault is -infinity, give upBound as 1 since all the max scheduled energy per hour is 1
      tmp.append(lp_var)
    lp_vars.append(tmp)
    

  # create functions for price in the form of price*user/task combination for instance 5.913804588632*user1_task1_20 + 0.0

  for l in range(len(task_info_p)):
    for var in lp_vars[l]:
      price = unit_cost[int(var.name.split('_')[2])]
      price_const.append(price * var)
  model_f += lpSum(price_const)

  for m in range(len(task_info_p)): # add the energy demand to the equation
    tmp2 = []
    for var in lp_vars[m]:
      tmp2.append(var)

     
    model_f += lpSum(tmp2) == task_info_p[m][3]


  return model_f

def plot(model_p,i_p):

  hours = [str(x) for x in range(0, 24)]
  pos = np.arange(len(hours))
  user_list = ['user1', 'user2', 'user3', 'user4', 'user5']
  color_list = ['red','blue','yellow','green','pink']
  plot_list = []
  #Create lists to plot usage
  for user in user_list:
      tmp3 = []
      for hour in hours:
          tmp4 = []
          for var in model_p.variables():
              if user == var.name.split('_')[0] and str(hour) == var.name.split('_')[2]: # if username and hour matches
                  tmp4.append(var.value())
          tmp3.append(sum(tmp4))
      plot_list.append(tmp3)

  plt.bar(pos,plot_list[0],color=color_list[0],edgecolor='black',bottom=0)
  plt.bar(pos,plot_list[1],color=color_list[1],edgecolor='black',bottom=np.array(plot_list[0]))
  plt.bar(pos,plot_list[2],color=color_list[2],edgecolor='black',bottom=np.array(plot_list[0])+np.array(plot_list[1]))
  plt.bar(pos,plot_list[3],color=color_list[3],edgecolor='black',bottom=np.array(plot_list[0])+np.array(plot_list[1])+np.array(plot_list[2]))
  plt.bar(pos,plot_list[4],color=color_list[4],edgecolor='black',bottom=np.array(plot_list[0])+np.array(plot_list[1])+np.array(plot_list[2])+np.array(plot_list[3]))
  
  plt.xticks(pos, hours)
  plt.xlabel('Hour')
  plt.ylabel('Energy Usage')
  plt.title('Energy Usage Per Hour For All Users\n' + str(i_p))
  plt.legend(user_list,loc=0)
  plt.show()
  images_dir = '/content/drive/My Drive/plots/'
  #plt.savefig(f'{images_dir}' + str(i_p) + ".png")

for i in range(len(x_test)): #iterate through test data
    if y_test[i] == 1: # if the predicted label is abnormal

      model = model_maker(user_tasks,task_info) #pulp lp model generation

      model.solve()

      plot(model,i+1)