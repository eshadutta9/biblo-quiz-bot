import sys
from os.path import join, abspath, dirname

# Get the directory of the current script
current_script_directory = dirname(abspath(__file__))

# Define the path to the desired directory
desired_directory = join(current_script_directory, 'machine-learning-model')

# Add the directory to the Python path
sys.path.append(desired_directory)
print(sys.path)