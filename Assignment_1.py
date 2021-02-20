'''
Title	 : Assignment-1
Purpose  : To read a .netlist file given by the user and verify and display the Spice codes in the the netlist file in reverse order
Author   : Surya Prasad S
Date     : 17th Nov 2021
Inputs   : '.netlist' file
Outputs  : Identifies and locates errors if there are any in the Spice codes (starts with .circuit and ends with .end) in the netlist files and displays the codes in reverse order (without the comments)
'''


# Importing libraries
import sys
import os

# Constants used in the code
INPUT_FILE_TYPE = '.netlist'	# Extension of netlist files
SPICE_BEGIN = '.circuit'		# Line which indicates start of Spice code
SPICE_END = '.end'				# Line which indicates end of Spice code


# Checking for Valid commandline arguments

## The number of commandline arguments is restricted to 2 - this python file and the netlist file
if len(sys.argv) != 2:
	print("Invalid number of arguments given. One file needs to be given.")
	exit()

file_input = sys.argv[1]

## Here the type of file being entered is checked
if file_input[-8:] != INPUT_FILE_TYPE:
	print("Incorrect file type. Only '.netlist' type files are accepted.")
	exit()

## Checking if the file given by the user exists and is read if it exists
try:
	f = open(file_input)
	lines = f.readlines()
#	print(lines)		# This can be uncommented to see the lines being read

except:
	print("Unable to locate file.")
	exit()

f.close()		# File is closed


# Function to check if a string can be converted into float
def check_scientific_notation(value_string):
	## An attempt is made to convert into float and if succesful, True is returned
	try:
		get_value = float(value_string)
		return True

	## If the attempt fails, False is returned
	except:
		return False		


# Checking if spice codes are present in the netlist file. 
no_circuit = True		# Checks if there is a Spice code in the netlist file
Begin_circuit = 0		# Stores the line at which a Spice code starts. Default value is 0 which is used to check if a Spice code has started.


for i in range(len(lines)):
	## Removing the comments and trailing whitespaces. Note that there cannot be components with names containing '#'. 
	if lines[i].find('#') >= 0:
		lines[i] = lines[i][:lines[i].find('#')]
	
	lines[i] = lines[i].strip()

	## Searching for SPICE_BEGIN in the netlist file which indicates the start of the Spice code
	if lines[i] == SPICE_BEGIN:
		if Begin_circuit == 0:	
			Begin_circuit = i+1

		else:
			print("Error: Previous Spice code which started at", Begin_circuit,"hasn't ended before the new start of another one at", i+1)
 
	## Searching for SPICE_END in the netlist file which indicates the end of the Spice code which starts at line Begin_circuit

	if lines[i] == SPICE_END:
		if Begin_circuit > 0:
			no_circuit = False
			Begin_circuit = 0

		else:
			print("Error: Encountered end of a Spice code at line", i+1,"without the start of a Spice code.")
			exit()


## If a Spice code hasn't been ended, then it prints an error
if Begin_circuit != 0:
	print("Error: End of Spice code missing for Start code present at line", Begin_circuit)
	exit()

## If a Spice code was not found in the netlist file then it prints an error. 
### This is not executed if the previous 'if' block is executed so it prints if there is no SPICE_BEGIN or SPICE_END
if no_circuit:
	print("The given netlist file has no identifiable Spice code.")
	exit()


# Here I am classifying the types of components on the basis of number and type of nodes
element_type1 = ['R','L','C','V','I']
element_type2 = ['E','G']
element_type3 = ['H','F']


# Defining a Class Component to store the tokens.
## Function check_validity validates data stored regarding a component. 
## The number of ports and dependencies need to be checked before passing them to an object of this Class
class Component:
	## Details about a component are to be stored in these variables
	component_type = None
	component_name = None
	component_ports = []
	component_dependencies = []
	component_value = None

	## Function to check validity of given tokens
	def check_validity(self, index = None):
		### Checking if the Port names are alpha-numeric
		for port_name in self.component_ports:
			if not port_name.isalnum():
				print("Error: Invalid Port name (" , port_name, ") at line" , index, "in the netlist file")
				print("\nOnly alpha-numeric node names are allowed")
				exit()

		### Checking for valid values
		if not check_scientific_notation(self.component_value):
			print("Error: Invalid value (", self.component_value,") at line", index, "in the netlist file")
			print("\nOnly alpha-numeric node names are allowed")
			exit()

		### Checking for dependencies
		if self.component_type in element_type3:
			if self.component_dependencies[0][0] != 'V':
				print("Error: Invalid dependency (", self.component_dependencies,") at line", index,".\nDependencies of current controlled sources need to start with V")
				exit()

	## Function to initialise an object of class Component
	def __init__(self, init_name = None, init_ports = [], init_dependencies = [], init_value = None):
		self.component_type = init_name[0]
		self.component_name = init_name
		self.component_ports = init_ports
		self.component_dependencies = init_dependencies
		self.component_value = init_value


# List to collect all the different and valid circuits. 
## This variable is used only for storing purpose and not used in this code. It can be used for further analysis of individual circuits or for group analysis.
collect_circuits = []


# Parsing each line and extracting tokens
for i in range(len(lines)-1):
	## Searching for SPICE_BEGIN in the netlist file
	if lines[i] == SPICE_BEGIN:
		circuit_components = []		# Variable to store the components and their tokens
		spice_lines = []			# Variable to store the lines of the spice code line by line for display purpose

		## If SPICE_BEGIN has been identified the lines are syntactically checked till a SPICE_END has been encountered
		for j in range(i+1,len(lines)):
			words = lines[j].split()		# Variable to store each line as a word array

			if len(words) == 0:		# If there are no words in the line, then we move to the next line
				continue

			### Each line is checked if its the end of the Spice code starting at i
			if words[0] == SPICE_END:
				collect_circuits.append(circuit_components)
				print("\n\nSpice code starting at line", i+1,"verified.\n")
				i = j+1		# This speedens up the searching for all the Spice codes in the netlist file
				break


			### First, the component which the line of code is dealing with is identified based on the name of the component
			### Second, the number of nodes is fixed according to the type of the component.
			### Third, the function check_validity is called to validate the tokens passed to the Component object
			
			element_name = words[0]			# All the components have the first their name as the first token

			#### Checking of components of type 1
			if words[0][0] in element_type1:
				if len(words) == 4:
					element_ports = [words[1], words[2]]
					element_dependencies = []
					element_value = words[3]

				else:
					print("Error: Incorrect syntax at line", j+1,". Incorrect set of tokens given for the component.")
					exit()					

			#### Checking of components of type 2
			elif words[0][0] in element_type2:
				if len(words) == 6:
					element_ports = [words[1], words[2], words[3], words[4]]
					element_dependencies = []
					element_value = words[5]

				else:
					print("Error: Incorrect syntax at line", j+1,". Incorrect set of tokens given for the component.")
					exit()					

			#### Checking of components of type 3
			elif words[0][0] in element_type3:
				if len(words) == 5:
					element_ports = [words[1], words[2]]
					element_dependencies = [words[3]]
					element_value = words[4]

				else:
					print("Error: Incorrect syntax at line", j+1,". Incorrect set of tokens given for the component.")
					exit()

			#### If the type of component is not valid
			else:
				print("""Error: Type-error in the type of component in line""", j+1,""".
					Accepted types are Resistor(R), Capacitor(C), Inductor(I), Voltage source(V), Current source(I), VCVS(E), VCCS(G), CCVS(H) and CCCS(F).
					The component's name should start with the given associated character.""")
				exit()


			### All the values are stored in the class object and the tokens are checked for their validity.
			component_details = Component(element_name, element_ports, element_dependencies, element_value)
			component_details.check_validity(j+1)

			### If check_validity() failed then the program exits. So the component details are stored only if it has passed.
			circuit_components.append(component_details)


			### The code lines are now processed as required for display purpose.

			#### Words of a line are reversed and a temporary string is being declared for converting array of strings into one string
			words.reverse()
			temporary_string = ""

			#### Words are being stored as strings for display purpose
			for eachword in words:
				temporary_string += eachword + ' '

			temporary_string = temporary_string[:-1]		# Space at the end is removed

			### Each line is being stored in spice_lines as type string
			spice_lines.append(temporary_string)


		## Order of lines is reversed for display purpose and displayed
		spice_lines.reverse()

		## Displaying output
		print("Displaying the modified Spice code")
		for spice_code in spice_lines:
			print(spice_code)

		print("\n")


'''
Brief Overview:
	1. Check for equal number of SPICE_BEGIN and SPICE_END and in that order.
	2. Then we read every line in a Spice code and verify their syntax based on their type.
	3. Verified code is stored in lists and component-wise tokens are stored separately in object of type Component.
	4. The list variables are used for display purpose and the 
	4. The code stored in lists is then displayed in reverse order.

In C code, I would have done similar blocks of code but it would have taken more number of lines.
Well-known codes like sort function may be inefficient as compared to the same pre-defined functions in python.
C code is also not capable of handling bad inputs as it is not a interpreter file.
This can be handled and taken advantage of in Python. For example, Python can identify strings which can be converted as float (strings with only numbers or numbers in scientific notation)
'''
