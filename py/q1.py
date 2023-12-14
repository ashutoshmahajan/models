# Python code for the quadratic optimization problem:
# min x1^2 - 2x1 + 1

from pyomo.environ import *

model = m = ConcreteModel()

m.x1 = Var(within=Reals)

m.obj = Objective(sense=minimize, expr= (m.x1**2 - 2*m.x1 + 1))

