#!/usr/bin/env python
# coding: utf-8


from pyomo.environ import *


import random
import numpy as np
import pandas as pd


#Generating the items weights. we are using normal distribution
# so that we can verify later if the model is working correctly.
def item_gen(mean,std,n):
    

  # Generate n random values from a normal distribution with mean and std
    values = np.random.normal(loc=mean, scale=std, size=n)

  # Clip the values between 1 and 100
    values = np.clip(values, 1, 100)

  # Convert the values to integers
    values = values.astype(int)

  #convert to a 1 - n indexed dataframe
    ind = range(1,n+1)
    df = pd.DataFrame(values, index = ind, columns = ["item size"])


    return df

np.random.seed(9)
item_gen(50,25,20)


m = AbstractModel()

#defining in the indexes
m.I = RangeSet(1,15)
m.J = RangeSet(1,20)

#defining the parameters
m.a = Param(m.J, within=NonNegativeIntegers, initialize=item_gen(50,25,20) )

#defining variables
m.x = Var(m.J, m.I, domain=Binary )
m.w = Var(m.I, domain =Binary)

#defining objective function

def obj_fun(m):
    return summation(m.w)

m.Obj = Objective(rule=obj_fun, sense=minimize)

#defining and declaring constraints

def axw_const(m,i):
  #for a given one i the expression should be
    return sum(m.a[j] * m.x[j,i] for j in m.J ) <= 100*m.w[i]

def x_const(m,j):
  #same constraint for j items so indexed over i
    return sum(m.x[j,i] for i in m.I) == 1

#now to iterate this same form constraint I number of times

m.AxwConst = Constraint(m.I, rule = axw_const)
m.XConst = Constraint(m.J, rule=x_const)

#constructing the instance
inst = m.create_instance()

inst.pprint()


opt = SolverFactory('mbnb', executable="C:/msys64/home/Olympus/minotaur/build/bin/mbnb.exe")


results = opt.solve(inst, tee=True)





