from pyomo.environ import *
import os
import importlib
import sys


## SET THESE PARAMETERS BEFORE EVERY RUN

solver_options = {'--bnb_time_limit': 60, '--log_level':3}
echo_out = True
me = "run.py:"

## End of parameters

def print_usage():
	print("usage: python run.py model.py /path/to/solver")
	print()
	print("edit run.py to change the solver or its parameters")


## Start the main code

if (len(sys.argv)<3):
	print_usage()
	sys.exit(1)

model_file = sys.argv[1]
solverpath = sys.argv[2]
print(me, "Solving", model_file)

infile = os.path.splitext(os.path.basename(model_file))[0]
try:
	# Import the Pyomo model class
	model = importlib.import_module(infile)
except ModuleNotFoundError as e:
	print(f"{me} Error importing module {infile}: {e}")
	sys.exit(1)

solver = SolverFactory("mglob", executable=solverpath)

for option, value in solver_options.items():
	solver.options[option] = value

# Extract instance name from the model file
instance_name = os.path.splitext(os.path.basename(model_file))[0]

try:
	result = solver.solve(model.m, tee=echo_out)
	print(f"\nResults for {model_file} : ")
	print("Solver termination status:",result.solver.status)
	print("Solver termination condition: {}".format(result.solver.termination_condition))
	print("Best solution value: {}".format(model.m.obj()))
	print("Best bound: {}".format(result.problem.lower_bound))
	print("Solver time: {}".format(result.solver.time))
except Exception as e:
	print(me, "Error solving", instance_name, ". Could not load results.")



