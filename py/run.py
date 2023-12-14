from pyomo.environ import *
import os
import importlib
import sys


## SET THESE PARAMETERS BEFORE EVERY RUN

model_file = "q1.py"
solverpath = "/home/amahajan/minotaur/build/bin/mglob"
solver_options = {'--bnb_time_limit': 60}
echo_out = False

## End of parameters

print("Solving", model_file)


infile = os.path.splitext(os.path.basename(model_file))[0]
print(infile)
try:
	# Import the Pyomo model class
	model = importlib.import_module(infile)
except ModuleNotFoundError as e:
	print(f"Error importing module {infile}: {e}")
	sys.exit(1)

solver = SolverFactory("mglob", executable=solverpath)

for option, value in solver_options.items():
	solver.options[option] = value

# Extract instance name from the model file
instance_name = os.path.splitext(os.path.basename(model_file))[0]

try:
	result = solver.solve(model.m, tee=echo_out)
	with open(output_file, "w") as f:
		f.write("**************************************************************")
		f.write(f"\nResults for {model_file} : ")

		if result.solver.status == SolverStatus.ok:
			f.write("Solver terminated successfully.")
		elif result.solver.status == SolverStatus.aborted:
			f.write("Solver reached the time limit.")
		else:
			f.write("Solver did not terminate successfully")

		f.write("\nSolver status: {}".format(result.solver.status))
		f.write("\nBest solution value obtained before the time limit: {}".format(model.m.obj()))
		f.write("\nSolver termination condition: {}".format(result.solver.termination_condition))
		f.write("\nSolver time: {}".format(result.solver.time))
		f.write("\nBest bound: {}".format(result.problem.lower_bound))
		f.close()
except Exception as e:
	print("Error solving", instance_name, ". Could not load results.")



