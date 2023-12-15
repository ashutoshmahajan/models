# Python code for the quadratic infeasible problem:
# min x1^2 + 2x1 + 5
# x1 integer
# X1 <= 0 and x1 >= 1

from pyomo.environ import *

model = m = ConcreteModel()

m.x1 = Var(domain = Integers )

m.constraint1 = Constraint(expr=(m.x1 <= 0))
m.constraint2 = Constraint(expr=(m.x1 >= 1))

m.obj = Objective(sense=minimize, expr= (m.x1**2 + 2*m.x1 + 5))
