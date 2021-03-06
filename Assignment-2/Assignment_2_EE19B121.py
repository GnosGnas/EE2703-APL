'''
Title	 : Assignment-2
Purpose  : To read and verify a .netlist file given by the user and to solve it and display the nodal voltages and currents passing through independent voltage sources
Author   : Surya Prasad.S(EE19B121) 
Date     : 3rd March 2021
Inputs   : '.netlist' file
Outputs  : Identifies and locates errors if there are any in the netlist file and displays the nodal voltages and currents passing through independent voltage sources
'''


# Importing libraries
import sys
import os
import numpy as np 
import math
import cmath


# Constants used in the code
INPUT_FILE_TYPE = '.netlist'	# Extension of netlist files
SPICE_BEGIN = '.circuit'		# Directive indicating start of Spice code
SPICE_END = '.end'				# Directive indicating end of Spice code
SPICE_AC = '.ac' 				# Directive containing the frequency of an AC source and also used to indicate the type of circuit
SPICE_DC = '.dc'				# Used to indicate the type of circuit

MAX_FLOAT = sys.float_info.max * 1e-100		# Slightly lesser than python's maximum value to prevent errors
MIN_FLOAT = sys.float_info.min * 1e100  	# Slightly more than python's maximum value to prevent errors 
PI = np.pi 									# Storing value of pi as another constant
THRESHOLD = float('1e-10')					# If a value falls below this threshold, then it is made 0


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


# Here I am classifying the types of components on the basis of number and type of nodes
## These lists are used only for pure DC circuit 
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

		### Checking for dependencies
		if self.component_type in element_type3:
			if self.component_dependencies[0][0] != 'V':
				print("Error: Invalid dependency (", self.component_dependencies,") at line", index,".\nDependencies of current controlled sources need to start with V")
				exit()

	## Function to initialise an object of class Component
	### Component's value is checked if its complex and has been converted into real when we deal with DC circuits
	def __init__(self, init_name = None, init_ports = [], init_dependencies = [], init_value = None):
		self.component_type = init_name[0]
		self.component_name = init_name
		self.component_ports = init_ports
		self.component_dependencies = init_dependencies

		try:
			self.component_value = complex(init_value)
		except:
			print("Error: Invalid value given for", init_name,"in the netlist file")
			print("\nValue has to be specified as a numeric or a string in scientific notation")
			exit()


# Function to solve linear equations given in the form of a matrix
## If the solution is not unique then a Bool value will be returned instead of a vector
def Solve_Linear_Equations(A_matrix, B_vector):
	try:
		vector_result = np.linalg.solve(A_matrix, B_vector)

	except:
		vector_result = False

	return vector_result


# Function to solve a purely DC circuit given the circuit's components
def Solve_DC(circuit_components):
	node_names = []			# List to store all the given node names and pseudo nodes (for current through voltage sources)

	## For loop to identify size of MNA matrix
	### Here I am including ground and later adding an equation V_GND = 0
	for element in circuit_components:
		for port in element.component_ports: 
			if ('V_' + port) not in node_names:
				node_names.append('V_' + port)

		
		### Pseudo nodes are being identified and added here and are given the name 'I_'+'node_name'
		if element.component_type == 'V' or element.component_type == 'E' or element.component_type == 'H': # Need to do for controlled voltage sources
			node_names.append('I_' + element.component_name)

	## Numpy arrays are mutable data-types so size was pre-determined
	mna_size = len(node_names)
	b_vector = np.zeros((mna_size, 1), dtype = complex)				# All values are being treated as complex for compatibility 
	mna_matrix = np.zeros((mna_size, mna_size), dtype = complex)

	## For loop to Populate MNA matrix and the corresponding B vector
	for element in circuit_components:
		node1 = node_names.index('V_' + element.component_ports[0])
		node2 = node_names.index('V_' + element.component_ports[1])

		### Resistor's value is being added to the matrix
		if element.component_type == 'R':
			mna_matrix[node1, node1] += 1/element.component_value
			mna_matrix[node1, node2] -= 1/element.component_value

			mna_matrix[node2, node2] += 1/element.component_value
			mna_matrix[node2, node1] -= 1/element.component_value

		### Inductor's value is being added to the matrix. Here I am adding a factor to make its effective resistance at steady state close to 0.
		elif element.component_type == 'L':
			mna_matrix[node1, node1] += 1/(MIN_FLOAT * element.component_value)
			mna_matrix[node1, node2] -= 1/(MIN_FLOAT * element.component_value)

			mna_matrix[node2, node2] += 1/(MIN_FLOAT * element.component_value)
			mna_matrix[node2, node1] -= 1/(MIN_FLOAT * element.component_value)		

		### Capacitor's value is being added to the matrix. Here I am adding a factor to make its effective resistance at steady state extremely large.
		elif element.component_type == 'C':
			mna_matrix[node1, node1] += (MIN_FLOAT * element.component_value)
			mna_matrix[node1, node2] -= (MIN_FLOAT * element.component_value)

			mna_matrix[node2, node2] += (MIN_FLOAT * element.component_value)
			mna_matrix[node2, node1] -= (MIN_FLOAT * element.component_value)	
		
		### Voltage source's value is being added to the the vector and the matrix is also modified.
		#### Here I am assuming the first node to be at higher potential and the current flowing from the first node
		elif element.component_type == 'V': 
			pseudo_node = node_names.index('I_' + element.component_name)

			mna_matrix[node1, pseudo_node] -= 1
			mna_matrix[node2, pseudo_node] += 1

			mna_matrix[pseudo_node, node1] += 1
			mna_matrix[pseudo_node, node2] -= 1		

			b_vector[pseudo_node] += element.component_value

		### Current source's value is being added to the the vector
		#### Here I am assuming that the current is flowing from the first node
		elif element.component_type == 'I':
			b_vector[node1] -= element.component_value
			b_vector[node2] += element.component_value

		### VCVS's value is being added to the matrix.
		#### Here I am assuming the first node to be connected to positive terminal and the first dependent node to be at higher potential
		elif element.component_type == 'E':
			pseudo_node = node_names.index('I_' + element.component_name)
			dependent_nodes = element.component_dependencies

			#### Checking if the dependencies are present
			if dependent_nodes[0] not in node_names or dependent_nodes[1] not in node_names:
				print("VCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, pseudo_node] -= 1
			mna_matrix[node2, pseudo_node] += 1

			mna_matrix[pseudo_node, node1] += 1
			mna_matrix[pseudo_node, node2] -= 1
			mna_matrix[pseudo_node, dependent_nodes[0]] -= element.component_value
			mna_matrix[pseudo_node, dependent_nodes[1]] += element.component_value

		### VCCS's value is being added to the matrix.
		#### Here I am assuming the current to flow from the first node to the second node and the first dependent node to be at higher potential
		elif element.component_type == 'G':
			dependent_nodes = element.component_dependencies

			#### Checking if the dependencies are present
			if dependent_nodes[0] not in node_names or dependent_nodes[1] not in node_names:
				print("VCCS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, dependent_nodes[0]] += element.component_value
			mna_matrix[node1, dependent_nodes[1]] -= element.component_value
	
			mna_matrix[node2, dependent_nodes[0]] -= element.component_value
			mna_matrix[node2, dependent_nodes[1]] += element.component_value

		### CCVS's value is being added to the matrix.
		#### Here I am assuming the first node to be connected to positive terminal
		elif element.component_type == 'H':
			pseudo_node = node_names.index('I_' + element.component_name)
			dependent_current = 'I_' + element.component_dependencies

			try:
				dependent_pseudo_node = node_names.index(dependent_current)

			except:
				print("CCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[pseudo_node, node1] += 1
			mna_matrix[pseudo_node, node2] -= 1

			mna_matrix[node1, dependent_pseudo_node] -= element.component_value

		### CCCS's value is being added to the matrix.
		#### Here I am assuming the current to flow from the first node to the second node
		elif element.component_type == 'F':
			dependent_current = 'I_' + element_dependencies

			try:
				dependent_pseudo_node = node_names.index(dependent_current)

			except:
				print("CCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, dependent_pseudo_node] += element.component_value
			mna_matrix[node2, dependent_pseudo_node] -= element.component_value


	## Additional modification to the matrix to make the potential of ground 0
	node_gnd = node_names.index('V_GND')
	mna_matrix[node_gnd, node_gnd] += 1

	## MNA matrix and vector are being passed to be solved. If it fails, then the function would return Boolean False instead of a vector
	result = Solve_Linear_Equations(mna_matrix, b_vector)

	## Checking type of result
	if type(result) == bool:
		print("Error: Inverse of matrix formed through MNA cannot be determined")
		exit()

	else:
		return result, node_names			# Both are sent for convenience sake


# Function to solve a circuit which may have AC components. In this code this is used such that there is only one active power source in the circuit
def Solve_AC(circuit_components, f):
	node_names = []					# List to store all the given node names and pseudo nodes (for current through voltage sources)

	## For loop to identify size of MNA matrix
	### Here I am including ground and later adding an equation V_GND = 0
	for element in circuit_components:
		for port in element.component_ports: # Gnd is included
			if ('V_' + port) not in node_names:
				node_names.append('V_' + port)

		### Pseudo nodes are being identified and added here and are given the name 'I_'+'node_name'
		if element.component_type == 'V' or element.component_type == 'E' or element.component_type == 'H': # Need to do for controlled voltage sources
			node_names.append('I_' + element.component_name)

	## Numpy arrays are mutable data-types so size was pre-determined
	mna_size = len(node_names)
	b_vector = np.zeros((mna_size, 1), dtype = complex)				# All values are being treated as complex for compatibility 
	mna_matrix = np.zeros((mna_size, mna_size), dtype = complex)

	## For loop to Populate MNA matrix and the corresponding B vector
	for element in circuit_components:
		node1 = node_names.index('V_' + element.component_ports[0])
		node2 = node_names.index('V_' + element.component_ports[1])

		### Resistor's value is being added to the matrix
		if element.component_type == 'R':
			mna_matrix[node1, node1] += 1/element.component_value
			mna_matrix[node1, node2] -= 1/element.component_value

			mna_matrix[node2, node2] += 1/element.component_value
			mna_matrix[node2, node1] -= 1/element.component_value

		### Inductor's value is being added to the matrix. Here I am adding a factor to make its effective resistance at steady state close to 0.
		elif element.component_type == 'L':
			mna_matrix[node1, node1] += 1/( (1j) * 2*PI*f * element.component_value )
			mna_matrix[node1, node2] -= 1/( (1j) * 2*PI*f * element.component_value )

			mna_matrix[node2, node2] += 1/( (1j) * 2*PI*f * element.component_value )
			mna_matrix[node2, node1] -= 1/( (1j) * 2*PI*f * element.component_value ) 					

		### Capacitor's value is being added to the matrix. Here I am adding a factor to make its effective resistance at steady state extremely large.
		elif element.component_type == 'C':
			mna_matrix[node1, node1] += ( (1j) * 2*PI*f * element.component_value )
			mna_matrix[node1, node2] -= ( (1j) * 2*PI*f * element.component_value )

			mna_matrix[node2, node2] += ( (1j) * 2*PI*f * element.component_value )
			mna_matrix[node2, node1] -= ( (1j) * 2*PI*f * element.component_value )

		### Voltage source's value is being added to the the vector and the matrix is also modified.
		#### Here I am assuming the first node to be at higher potential and the current flowing from the first node
		elif element.component_type == 'V':
			pseudo_node = node_names.index('I_' + element.component_name)

			mna_matrix[node1, pseudo_node] = -1
			mna_matrix[node2, pseudo_node] = 1

			mna_matrix[pseudo_node, node1] = 1
			mna_matrix[pseudo_node, node2] = -1		

			b_vector[pseudo_node] = element.component_value

		### Current source's value is being added to the the vector
		#### Here I am assuming that the current is flowing from the first node
		elif element.component_type == 'I':
			b_vector[node1] -= element.component_value
			b_vector[node2] += element.component_value

		### VCVS's value is being added to the matrix.
		#### Here I am assuming the first node to be connected to positive terminal and the first dependent node to be at higher potential
		elif element.component_type == 'E':
			pseudo_node = node_name.index('I_' + element.component_name)
			dependent_nodes = element.component_dependencies

			#### Checking if the dependencies are present
			if dependent_nodes[0] not in node_names or dependent_nodes[1] not in node_names:
				print("VCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, pseudo_node] = -1
			mna_matrix[node2, pseudo_node] = 1

			mna_matrix[pseudo_node, node1] = 1
			mna_matrix[pseudo_node, node2] = -1
			mna_matrix[pseudo_node, dependent_nodes[0]] = -(element.component_value)
			mna_matrix[pseudo_node, dependent_nodes[1]] = element.component_value

		### VCCS's value is being added to the matrix.
		#### Here I am assuming the first node to be connected to positive terminal and the first dependent node to be at higher potential
		elif element.component_type == 'G':
			dependent_nodes = element.component_dependencies

			#### Checking if the dependencies are present
			if dependent_nodes[0] not in node_names or dependent_nodes[1] not in node_names:
				print("VCCS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, dependent_nodes[0]] += element.component_value
			mna_matrix[node1, dependent_nodes[1]] -= element.component_value
	
			mna_matrix[node2, dependent_nodes[0]] -= element.component_value
			mna_matrix[node2, dependent_nodes[1]] += element.component_value

		### CCVS's value is being added to the matrix.
		#### Here I am assuming the first node to be connected to positive terminal
		elif element.component_type == 'H':
			pseudo_node = node_names.index('I_' + element.component_name)
			dependent_current = 'I_' + element.component_dependencies

			try:
				dependent_pseudo_node = node_names.index(dependent_current)

			except:
				print("CCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[pseudo_node, node1] += 1
			mna_matrix[pseudo_node, node2] -= 1

			mna_matrix[node1, dependent_pseudo_node] -= element.component_value

		### CCCS's value is being added to the matrix.
		#### Here I am assuming the current to flow from the first node to the second node
		elif element.component_type == 'F':
			dependent_current = 'I_' + element_dependencies

			try:
				dependent_pseudo_node = node_names.index(dependent_current)

			except:
				print("CCVS (", element.component_name, ") has invalid dependencies.")
				exit()

			mna_matrix[node1, dependent_pseudo_node] += element.component_value
			mna_matrix[node2, dependent_pseudo_node] -= element.component_value
		else:
			print("Not handled")
			exit()


	## Additional modification to the matrix to make the potential of ground 0
	node_gnd = node_names.index('V_GND')
	mna_matrix[node_gnd, node_gnd] += 1

	## MNA matrix and vector are being passed to be solved. If it fails, then the function would return Boolean False instead of a vector
	result = Solve_Linear_Equations(mna_matrix, b_vector)

	## Checking type of result
	if type(result) == bool:
		print("Error: Inverse of matrix formed through MNA not found")
		exit()

	else:
		return result, node_names			# Both are sent for convenience sake


# Checking if spice codes are present in the netlist file. 
no_circuit = True		# Checks if there is a Spice code in the netlist file
Begin_circuit = 0		# Stores the line at which a Spice code starts. Default value is 0 which is used to check if a Spice code has started.
source_frequencies = {} # Dictionary variable to store frequences of AC sources. Its used in other parts of the code for calculative purposes

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

	## Searching for SPICE_AC in the netlist file which contains the frequency of an AC source
	### It is checked if a block of Spice code was identified previously
	if lines[i][:3] ==  SPICE_AC:
		if Begin_circuit == 0 and not no_circuit:
			words = lines[i].split()

			if len(words) == 3 and ( words[1][0] == 'V' or words[1][0] == 'I'):
				if words[1] in source_frequencies:
					print("Error: Reassignment of frequency to AC source", words[1], "at line", i+1)
					exit()

				try:
					source_frequencies[words[1]] = float(words[2])
				except:
					print("Error: Specified frequency at line", i+1, "is not valid.")
					print("\nValue has to be specified as a numeric or a string in scientific notation")
					exit()
			else:
				print("Error: Syntax error at line", i+1)
				exit()

		else:
			print("Error: Encountered an unexpected .ac directive at line", i+1)
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


# Function to solve a circuit of given type and display nodal voltages and currents through the voltage sources
## Here AC type circuit means that there 'might' have AC sources and DC type circuits have only DC sources
def Solve_circuit(circuit_components, circuit_type):

	## Solving for AC type circuit
	### Sources operating at multiple frequencies, including DC sources, have been accounted for
	if circuit_type == SPICE_AC:
		sources = {}			# Dictionary to store all independent power sources with their values
		final_result = {}		# Dictionary to store all the frequencies of the power sources with the MNA output values

		### For loop to store power sources and their values and to remove all the sources from the circuit to enable solving through superposition
		for element in circuit_components:
			if (element.component_type == 'V' or element.component_type == 'I'):
				sources[element.component_name] = element.component_value
				circuit_components[circuit_components.index(element)].component_value = 0


		### For loop to perform MNA by superposition by considering individual power sources
		#### Here same frequencies are added together and stored in final_result
		#### Though the loop needs to go only over those elements named in sources{}, the element object is required for indexing purposes.
		for element in circuit_components:

			if element.component_name in sources:
				circuit_components[circuit_components.index(element)].component_value = sources[element.component_name]

				frequency = source_frequencies[element.component_name]					# Variable to act like an alias

				if frequency == 0:
					temp_result, node_names = Solve_DC(circuit_components)				# Temporary variables to get the values

				else:
					temp_result, node_names = Solve_AC(circuit_components, frequency)	# Temporary variables to get the values

				circuit_components[circuit_components.index(element)].component_value = 0			

				if frequency in final_result:
					final_result[frequency] += temp_result

				else:
					final_result[frequency] = temp_result


		### Displaying all the unknown voltages of the nodes and currents passing through voltage source
		print("Modified Nodal Analysis has been performed successfully.")
		print("Voltage of GND node is taken as 0 for reference\n")


		#### For loop for displaying each nodal voltage
		##### Multiple if statements used to address various cases
		for node in node_names:
			if node[0] == 'V' and node != 'V_GND':
				nodal_voltages = {node:[]}

				for source_name in source_frequencies:
					nodal_voltages[node].append([ source_frequencies[source_name] , final_result[source_frequencies[source_name]][node_names.index(node)][0] ])

				print("Voltage at node", node[2:], "is ", end="")

				for i in range(len(nodal_voltages[node])):
					omega = 2 * PI * nodal_voltages[node][i][0]
					voltage = nodal_voltages[node][i][1]
					magnitude = abs(voltage)
					phase = cmath.phase(voltage) * (180/PI)
					
					if magnitude < THRESHOLD:
						magnitude = float(0)
						phase = float(0)

					if abs(phase) < THRESHOLD:
						phase = float(0)

					if phase != 0:
						print("{:.3}*cos({:.3}t+({:.3} deg))".format(magnitude, omega, phase),sep='', end='')

					else:
						if magnitude != 0:
							if omega != 0:
								print("{:.3}*cos({:.3}t)".format(magnitude, omega),sep='', end='')

							else:
								print("{:.3}".format(magnitude),sep='', end='')

						else:
							print("0",sep='', end='')

					if i != len(nodal_voltages[node])-1:
						print(' + ', end="")
					else:
						print(" V")


		#### For loop for displaying each current passing through voltage source
		##### Multiple if statements used to address various cases
		for node in node_names:
			if node[0] == 'I':
				currents = {node:[]}

				for source_name in source_frequencies:
					currents[node].append([ source_frequencies[source_name] , final_result[source_frequencies[source_name]][node_names.index(node)][0] ])

				print("Current passing through the source", node[2:], "is ", end="")

				for i in range(len(currents[node])):
					omega = 2 * PI * currents[node][i][0]
					current = currents[node][i][1]
					magnitude = abs(current)
					phase = cmath.phase(current) * (180/PI)

					if magnitude < THRESHOLD:
						magnitude = float(0)
						phase = float(0)

					if abs(phase) < THRESHOLD:
						phase = float(0)

					if phase != 0:
						print("{:.3}*cos({:.3}t+({:.3} deg))".format(magnitude, omega, phase),sep='', end='')

					else:
						if magnitude != 0:
							if omega != 0:
								print("{:.3}*cos({:.3}t)".format(magnitude, omega),sep='', end='')

							else:
								print("{:.3}".format(magnitude),sep='', end='')

						else:
							print("0",sep='', end='')

					if i != len(currents[node])-1:
						print(' + ', end="")
					else:
						print(" A")

	else:
		final_result, node_names = Solve_DC(circuit_components)

		### Displaying all the unknown voltages of the nodes and currents passing through voltage source
		print("MNA has been performed successfully.")
		print("Voltage of GND node is taken as 0 for reference\n")


		#### For loop for displaying each nodal voltages
		for node in node_names:
			if node[0] == 'V' and node != 'V_GND':
				print("Voltage at node", node[2:], "is {:.3} V".format(final_result[node_names.index(node)][0].real))


		#### For loop for displaying each current passing through voltage source
		for node in node_names:
			if node[0] == 'I':
				print("Current passing through the source", node[2:], "is {:.3} A".format(final_result[node_names.index(node)][0].real))



# List to collect all the different and valid circuits. 
## This variable is used only for storing purpose and is not used in this code. It can be used for analysing multiple circuits (if its possible)
collect_circuits = []

# Parsing each line and extracting tokens
for i in range(len(lines)-1):
	## Searching for SPICE_BEGIN in the netlist file
	if lines[i] == SPICE_BEGIN:
		circuit_components = []		# Variable to store the components and their tokens
		spice_lines = []			# Variable to store the lines of the spice code line by line for display purpose
		element_array = []			# Variable to collect all the names of the elements to prevent redefinition
		FLAG_GND = False 			# Variable to indicate if node GND is present

		## If SPICE_BEGIN has been identified the lines are syntactically checked till a SPICE_END has been encountered
		for j in range(i+1,len(lines)):
			words = lines[j].split()		# Variable to store each line as a word array

			if len(words) == 0:		# If there are no words in the line, then we move to the next line
				continue

			### Each line is checked if its the end of the Spice code starting at i
			if words[0] == SPICE_END:
				if not FLAG_GND:			# If GND node wasn't found then error is displayed
					print("Error: No component connected to GND found.")
					exit()

				collect_circuits.append(circuit_components)
				print("\nSpice code starting at line", i+1,"verified.\n")
				break ##
			
			element_name = words[0]			# All the components have the first their name as the first token

			### First, it is checked if the identified Spice code is for an AC circuit by checking if the number of AC sources is more than 0
			#### If true, a different syntax is checked for voltage and current sources based on if its AC or DC
			#### The DC component is also stored in source_frequencies{} with frequency as 0
			if len(source_frequencies) != 0 and ( words[0][0] == 'V' or words[0][0] == 'I'):
				if words[3] == 'ac' and len(words) == 6:
					if words[0] not in source_frequencies:
						print("Error: AC source with unassigned frequency at line", j+1)
						exit()

					else:
						element_ports = [words[1], words[2]]

						try:
							phase = float(words[5])
						except:
							print("Error: Phase value given incorrectly at line", j+1)
							exit()

						element_dependencies = []
						element_value = float(words[4]) * np.exp(1j*PI*(phase/180)) * 0.5

				elif words[3] == 'dc' and len(words) == 5:
					element_ports = [words[1], words[2]]
					element_dependencies = []
					element_value = words[4]

					source_frequencies[element_name] = 0

				else:
					print("Error: Incorrect syntax for power source at line", j+1)
					exit()

			### Then onwards, we check with regular syntax (common to both AC and DC circuit) and also skip checking voltage and current sources if the circuit is an AC circuit

			#### Checking of components of type 1
			if words[0][0] in element_type1:
				if len(source_frequencies) != 0 and ( words[0][0] == 'V' or words[0][0] == 'I'):
					if words[3] == 'ac' and len(words) == 6:
						if words[0] not in source_frequencies:
							print("Error: AC source with unassigned frequency at line", j+1)
							exit()

						else:
							element_ports = [words[1], words[2]]

							try:
								phase = float(words[5])
							except:
								print("Error: Phase value given incorrectly at line", j+1)
								exit()

							element_dependencies = []
							element_value = float(words[4]) * np.exp(1j*PI*(phase/180)) * 0.5

					elif words[3] == 'dc' and len(words) == 5:
						element_ports = [words[1], words[2]]
						element_dependencies = []
						element_value = words[4]

					else:
						print("Error: Incorrect syntax for power source at line", j+1)
						exit()

				elif len(words) == 4:
					element_ports = [words[1], words[2]]
					element_dependencies = []
					element_value = words[3]

				else:
					print("Error: Incorrect syntax at line", j+1,". Incorrect set of tokens given for the component.")
					exit()					

			#### Checking of components of type 2
			elif words[0][0] in element_type2:
				if len(words) == 6:
					element_ports = [words[1], words[2]]
					element_dependencies = [words[3], words[4]]
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

			### Checking if any element is being redefined
			if element_name in element_array:
				print("Error: Redefinition of", element_name," at line", j+1)
				exit()

			else:
				element_array.append(element_name)

			### If GND node is encountered, flag is set True
			if element_ports[0] == 'GND' or element_ports[1] == 'GND':
				FLAG_GND = True


			### All the values are stored in the class object and the tokens are checked for their validity.
			component_details = Component(element_name, element_ports, element_dependencies, element_value)
			component_details.check_validity(j+1)

			### If check_validity() failed then the program exits. So the component details are stored only if it has passed.
			circuit_components.append(component_details)

		### After all the elements have been collected, then we pass it to Solve_circuit() along with the parameter to tell if its an AC or DC circuit
		if len(source_frequencies) != 0:
			Solve_circuit(circuit_components, SPICE_AC)

		else:
			Solve_circuit(circuit_components, SPICE_DC)

		exit()