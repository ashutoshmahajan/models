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
header, stock_data

#converting the values list into np array for statistical calculations 
for head, series in stock_data.items():
    stock_data[head] = np.array(series)
stock_data


#assuming time period t to control period of return estimation
t = 2
#Building percent change(ratio) array of returns over time period t
stock_pct = np.array([(series[t:] - series[:-t])/series[:-t] for series in stock_data.values()])
stock_pct[0]



#calculating mean of returns for each stock
means = np.mean(stock_pct, axis=1)
#calculating variance of stocks against each other
cov_matrix = np.cov(stock_pct)
header,means,cov_matrix


from pyomo.environ import *

# Create a model
model = ConcreteModel()

# Number of assets
n_assets = len(means)  # Replace 'means' with your mean returns array

# Variables: Portfolio weights for each asset, bounded between 0 and 1
model.w = Var(range(n_assets), domain=NonNegativeReals, bounds=(0, 1))

# Objective: Minimize risk (variance) using sum_product for matrix multiplication
model.obj = Objective(expr=sum(model.w[i] * sum(cov_matrix[i, j] * model.w[j] for j in range(n_assets)) for i in range(n_assets)),
    sense=minimize
)

# Constraint: Sum of weights should be 1 (100% of the portfolio)
model.c1 = Constraint(expr=sum(model.w[i] for i in range(n_assets)) == 1)

model.pprint()


#Solve the model using a solver

opt = SolverFactory('mbnb', executable="C:/msys64/home/Olympus/minotaur/build/bin/mbnb.exe")
results = opt.solve(model, tee=True)
# Extract the solution
weights = [value(model.w[i]) for i in range(n_assets)]

# Output the minimum risk portfolio weights
print("Minimum Risk Portfolio Weights:", weights)


