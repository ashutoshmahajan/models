from pyomo.environ import *

model = m = ConcreteModel()

m.x1 = Var(domain = Integers )
m.x2 = Var(domain = Integers )


m.constraint1 = Constraint(expr=(m.x1 >= 0))
m.constraint2 = Constraint(expr=(m.x2 >= 0))
m.constraint3 = Constraint(expr=(m.x1 + m.x2 <= -1))
m.constraint4 = Constraint(expr=(2*m.x1 + 2*m.x2 >= 2))

m.obj = Objective(sense=minimize, expr= (m.x1**2 + m.x2**2))
