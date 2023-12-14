# Python code for the quadratic optimization problem:
# min 9x1^2 - 12x1 + 4
# x1 integer


from pyomo.environ import *

model = m = ConcreteModel()

m.x1 = Var(within=Integers)

m.obj = Objective(sense=minimize, expr= (9*m.x1**2 - 12*m.x1 + 4))

