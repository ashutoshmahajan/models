#!/usr/bin/env python
# coding: utf-8

import numpy as np
import time

#Funneling csv stock data into a dictionary of stock:values
with open("Closing_Prices_5yrs.csv") as f:
    lines = f.readlines()
    header = lines[0].strip().split(",")[1:]
    header = [names.replace(".csv","") for names in header]
    stock_data = {stock : [] for stock in header}
    lines = lines[1:]
    for line in lines:
        enteries = line.strip().split(",")[1:]
        for head, value in zip(header, enteries):
            if value:
                stock_data[head].append(float(value))
            else:
                stock_data[head].append(np.nan) #placeholder for empty values
                
            
print("Stock Companies:", header,"\n","Point data for first three companies:", list(stock_data.items())[:2] )

#converting the values list into np array for statistical calculations 
for head, series in stock_data.items():
    stock_data[head] = np.array(series)
stock_data
#handling nan files
def backward_fill(arr):
    '''Backward fills NaN values in a numpy array with the last valid observation.'''
    for i in range(1, len(arr)):
        if np.isnan(arr[i]):
            arr[i] = arr[i - 1]  # Replace NaN with the previous value
    return arr
for head, series in stock_data.items():
    stock_data[head] = backward_fill(np.array(series))



#assuming time period t to control period of return estimation
t = 2
print("Period of expectation time:", t, "\n")
#Building percent change(ratio) array of returns over time period t
stock_pct = np.array([(series[t:] - series[:-t])/series[:-t] for series in stock_data.values()])
print("%returns of stocks:", stock_pct, "\n", "array size:", stock_pct.shape, "\n")


#calculating mean of returns for each stock
means = np.mean(stock_pct, axis=1)
print("Mean %returns for stocks:", means*100, "\n") 
#calculating variance of each stock or risk
var = np.var(stock_pct, axis=1)
print("%Risk of individual stocks:", np.sqrt(var)*100, "\n")
#calculating c0-variance of stocks against each other
cov_matrix = np.cov(stock_pct)


from pyomo.environ import *

# Create a model
model = ConcreteModel()

# Number of assets
n_assets = len(means) 
#Number of companies to buy
k = 9
# Variables: Portfolio weights for each asset, bounded between 0 and 1
model.w = Var(range(n_assets), domain=NonNegativeReals, bounds=(0, 1))
#choice variable to select make number of stocks discrete
model.z = Var(range(n_assets), domain=Binary)


# Objective: Minimize risk (variance) using sum_product for matrix multiplication
model.obj = Objective(expr=sqrt(sum(model.w[i] * sum(cov_matrix[i, j] * model.w[j] for j in range(n_assets)) for i in range(n_assets))), sense=minimize)

# Constraint: Sum of weights should be 1 (100% of the portfolio)
model.c1 = Constraint(expr=sum(model.w[i] for i in range(n_assets)) == 1)
#choice = 1 means w >0 or else w<=0
def choice_zero(model,i,e = 10**-9):
    return e*model.z[i] <= model.w[i]
def choice_one(model,i):
    return model.w[i] <= model.z[i] 

model.c3 = Constraint(range(n_assets), rule=choice_zero)
model.c4 = Constraint(range(n_assets), rule= choice_one)
#choice decision
model.c5 = Constraint(expr=sum(model.z[i] for i in range(n_assets)) <= k)




#Solve the model using a solver

mntr = SolverFactory('mqg')
#Solve the model using a solver
#solver_options = {'--nlp_engine': 'IPOPT', '--log_level':6, '--display_problem':1} 
#for option, val in solver_options.items():
#	mntr.options[option] = val
time1 = time.time()
mntr.solve(model, tee=True)
time1end = time.time()
elapsed_time1 = time1end - time1
print(f"Minotaur took {elapsed_time1} seconds to solve the minimum risk")


chosen_stocks = []
choices = [round(value(model.z[i])) for i in range(n_assets)]
for hd, ch in zip(header,choices):
    if ch == 1:
        chosen_stocks.append(hd)

print("The chosen stocks for the Minimum portfolio are:",chosen_stocks) 


# Extract the solution
weights = [round(value(model.w[i])*100, 2) for i in range(n_assets)]
port = {}
for head, weight in zip(header, weights):
	port[head] = weight

# Output the minimum risk portfolio weights
print("Minimum Risk Portfolio percentage :", port)


sum_check= 0
for val in port.values():
    sum_check = sum_check+val
print("Sum Check for weights /100 :", sum_check)


#extracting portfolio risk
port_risk = value(model.obj)
print("Minimum Risk Portfolio risk %:", port_risk*100)
#extracting portfolio return
Port_return = 0
for returns, weight in zip(means, weights):
    Port_return = Port_return + returns*weight/100
print("Minimum Risk Portfolio return%:", Port_return*100)


#Building Efficient fronteir minimizing risk for different returns
expected_returns = [0.0015,0.0017, 0.0020,0.0021]
#Lists to store results
variances = [port_risk]
returns = [Port_return]

time2 = time.time()
#Defining a new constraint for minimum returns needed and iterating it
for target_return in expected_returns:
    model.c2 = Constraint( expr = sum(model.w[i]*means[i] for i in range(n_assets)) >= target_return)

    #solving the model
    mntr.solve(model, tee=True)
    
    #recording results
    variances.append(value(model.obj))
    returns.append(target_return)
time2end = time.time()
elapsed_time2 = time2end - time2
print(f"Minotaur took {elapsed_time2} seconds to solve for efficient fronteir")


effi_fronteir = {}
for ret, var in zip(returns, variances):
    effi_fronteir[ret*100] = var*100

print("Efficient (%returns : %risks) are:" , effi_fronteir)


#plotting the fronteir

import matplotlib.pyplot as plt
plt.plot(np.array(variances)*100, np.array(returns)*100,'-ro')
plt.xlabel("risk%")
plt.ylabel(f"returns% in {t} days")
plt.title(f"Efficiency Frontier Built Minimizing risk and Max Choice= {k}")
plt.grid()
plt.savefig('5yr_Markowitz_frontier.png')
plt.show()