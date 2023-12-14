# Python code for the quadratic optimization problem:
# min x1^2 + x2^2 + x3^2

from pyomo.environ import *

model = m = ConcreteModel()

m.x1 = Var(within=Reals)
m.x2 = Var(within=Reals)
m.x3 = Var(within=Reals)

m.obj = Objective(sense=minimize, expr= (m.x1**2 + m.x2**2 + m.x3**2))

