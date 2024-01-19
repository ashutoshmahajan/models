#!/usr/bin/env python
# coding: utf-8

import numpy as np

#Funneling csv stock data into a dictionary of stock:values
with open("Stock_Closing_Price.csv") as f:
    lines = f.readlines()
    header = lines[0][:-1].split(",")
    header = [names.replace(".csv","") for names in header]
    stock_data = {stock : [] for stock in header}
    lines = lines[1:]
    for line in lines:
        enteries = line[:-1].split(",")
        for head, value in zip(header, enteries):
            stock_data[head].append(float(value))
print("Stock Companies:", header,"\n","Point data for first three companies:", list(stock_data.items())[:2] )


#converting the values list into np array for statistical calculations 
for head, series in stock_data.items():
    stock_data[head] = np.array(series)
stock_data


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

# Variables: Portfolio weights for each asset, bounded between 0 and 1
model.w = Var(range(n_assets), domain=NonNegativeReals, bounds=(0, 1))

# Objective: Minimize risk (variance) using sum_product for matrix multiplication
model.obj = Objective(expr=sqrt(sum(model.w[i] * sum(cov_matrix[i, j] * model.w[j] for j in range(n_assets)) for i in range(n_assets))), sense=minimize)

# Constraint: Sum of weights should be 1 (100% of the portfolio)
model.c1 = Constraint(expr=sum(model.w[i] for i in range(n_assets)) == 1)


#Solve the model using a solver. Replace the given executable path according to your computer to mqg

mntr = SolverFactory('mqg', executable="/home/mohan/minotaur/build/bin/mqg")
mntr.solve(model, tee=True)


# Extract the solution
weights = [value(model.w[i])*100 for i in range(n_assets)]
port = {}
for head, weight in zip(header, weights):
	port[head] = weight

# Output the minimum risk portfolio weights
print("Minimum Risk Portfolio percentage :", port)


sum_check= 0
for val in port.values():
    sum_check = sum_check+val
sum_check


#extracting portfolio risk
port_risk = value(model.obj)
print("Minimum Risk Portfolio risk %:", port_risk*100)
#extracting portfolio return
Port_return = 0
for returns, weight in zip(means, weights):
    Port_return = Port_return + returns*weight
print("Minimum Risk Portfolio return%:", Port_return*100)


#Building Efficient fronteir minimizing risk for different returns
expected_returns = [0.0,0.00025, 0.0005, 0.001, 0.002, 0.004]
#Lists to store results
variances = [port_risk]
returns = [Port_return]

#Defining a new constraint for minimum returns needed and iterating it
for target_return in expected_returns:
    model.c2 = Constraint( expr = sum(model.w[i]*means[i] for i in range(n_assets)) >= target_return)

    #solving the model
    mntr.solve(model, tee=True)
    
    #recording results
    variances.append(value(model.obj))
    returns.append(target_return)


effi_fronteir = {}
for ret, var in zip(returns, variances):
    effi_fronteir[ret*100] = var*100

print("Efficient (%returns : %risks) are:" , effi_fronteir)


#plotting the efficient frontier

import matplotlib.pyplot as plt
plt.plot(np.array(variances)*100, np.array(returns)*100,'-ro')
plt.xlabel("risk%")
plt.ylabel("returns%")
plt.title("Efficiency Frontier Built Minimizing risk")
plt.grid()
plt.show
