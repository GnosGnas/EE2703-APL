'''
Title	 : Assignment-3
Purpose  : To fit a given set of values generated by a function which has errors
Author   : Surya Prasad.S(EE19B121) 
Date     : 3rd March2021
Inputs   : fitting.dat
Outputs  : Various plots to identify the best parameters
'''


# Importing libraries
import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.special as sp


# List of standard deviation of noise
sig = np.logspace(-1, -3, 9)

# True value
A_true = 1.05
B_true = -0.105

# Checking if the file exists and loading if true
## numpy.loadtxt() loads the values and stores directly in matrix form
try:
	file_data = np.loadtxt("fitting.dat")
except:
	print("Error: File 'fitting.dat' not found")
	exit()


# The first column holds time and the remaining columns hold the values generated by "generate_data.py"
x = file_data[:, 0]
y = file_data[:, 1:]


# Function to calculate the exact value corresponding to given time
def g(t, A, B):
	return A * sp.jn(2, t) + B * t


# Plotting of all the generated values and the actual value
labels = np.append(sig, "True Value")

## For loop to create required strings
for i in range(len(labels) - 1):
	labels[i] = "σ" + "$_" + str(i + 1) + "$" + "=" + str(round(sig[i], 3))


print("Plotting of f(t) vs t for no noise and for different noise values")
plt.figure(0)
plt.plot(x,y)
plt.plot(x,g(x, A_true, B_true), 'k', linewidth=3)
plt.grid(True)
plt.title(r'Q4: A Plot of f(t) vs t for different Noise Levels')
plt.xlabel('$t\\rightarrow$', size = 15)
plt.ylabel('$f(t)+noise\\rightarrow$', size = 15)
plt.legend(labels)
plt.show()


# Plotting of Errobar 
print("Errorbar is being plotted")
y_true = g(x, A_true, B_true)				# Actual value is being calculated
sigma = np.std(y[:, 0] - y_true)			# Standard deviation is being done
plt.plot(x, y_true, label = 'f(t)')
plt.errorbar(x[::5], y[::5, 0], sigma, fmt = 'ro', label = 'Errorbar')
plt.grid(True)
plt.title('Q5: Data points for σ = ' + str(sig[0]) + ' along with exact function')
plt.xlabel('$t\\rightarrow$', size = 15)
plt.legend()
plt.show()


# Construction of Matrix for the problem
M = np.c_[sp.jn(2, x), x]

## The matrix is being verified by multiplying it with the true values of A and B
if np.array_equal(np.dot(M, np.array([A_true, B_true])), g(x, A_true, B_true)):
	print("Error: Constructed matrix M is incorrect")
	exit()
else:
	print("Matrix M has been constructed and verified")


# Prediction of A and B parameters
## First we calculate the Mean Squared Error (MSE) for the given set of values

print("Mean Squared Error is being calculated")
a = np.linspace(0, 2, 21)
b = np.linspace(-0.2, 0, 21)

MSE = np.zeros((len(a), len(b)))

## For loop to calculate MSE for different A and B values
for i in range(len(a)):
	for j in range(len(b)):
		MSE[i, j] = ((y[:, 0] - g(x,a[i],b[j]))**2).mean(axis=0)


# Contour plot
## First we generate a meshgrid with the set of values of A and B
print("Contour Plot is being plotted")
XX, YY = np.meshgrid(a,b)
contour_levels = np.linspace(0.025, 0.5, 20)
CS = plt.contour(XX, YY, MSE, contour_levels)
plt.clabel(CS,CS.levels[:4], inline=1, fontsize=10)
plt.plot(1.05, -0.105, 'ro')
plt.annotate('Exact Value', (1.05, -0.105))
plt.title("Q8: Contour Plot of ε" + "$_" + "i" + "$" + "$_" + "j" + "$")
plt.xlabel('$A\\rightarrow$', size = 15)
plt.ylabel('$B\\rightarrow$', size = 15)
plt.show()


# Estimation and the corresponding error of A and B values
Estimations = []
Errors = []

## For loop to estimate for different columns in y
for i in range(np.size(y, 1)):
	Estimation_i,_,_,_ = np.linalg.lstsq(M, y[:, i], rcond=None)
	Error_i = [abs(Estimation_i[0] - 1.05), abs(Estimation_i[1] + 0.105)]

	Estimations.append(Estimation_i)
	Errors.append(Error_i)

## Converting the lists to numpy arrays for the sake of convenience
Estimations = np.array(Estimations)
Errors = np.array(Errors)


# Plotting of various plots for Error Analysis
print("Error Analysis:")

## Plotting of errors on an absolute scale
print("Plotting of errors on an absolute scale")
plt.plot(sig, Errors[:, 0], linestyle = '--', marker = 'o', color = 'r', label = 'Aerr')
plt.plot(sig, Errors[:, 1], linestyle = '--', marker = 'o', color = 'b', label = 'Berr')
plt.grid(True)
plt.title("Q10: Variation of error with noise")
plt.xlabel("$Noise\ Standard\ Deviation\\rightarrow$", size = 15)
plt.ylabel("$Mean\ Squared\ Error\\rightarrow$", size = 15)
plt.legend()
plt.show()

## Plotting of errors on logarithmic scale
print("Plotting of errors on logarithmic scale")
plt.loglog(sig,Errors[:, 0], linestyle = '--', marker = 'o', color = 'r', label = 'Aerr')
plt.loglog(sig,Errors[:, 1], linestyle = '--', marker = 'o', color = 'b', label = 'Berr')
plt.grid(True)
plt.title("Variation of error with noise in logarithmic scale")
plt.xlabel("$Noise\ Standard\ Deviation\\rightarrow$", size = 15)
plt.ylabel("$Mean\ Squared\ Error\\rightarrow$", size = 15)
plt.legend()
plt.show()

## Stem plotting of errors on logarithmic scale
print("Stem plotting of errors on logarithmic scale")
plt.loglog(sig, Errors[:, 0], linestyle = '', marker = 'o', color = 'r', label = 'Aerr')
plt.loglog(sig, Errors[:, 1], linestyle = '', marker = 'o', color = 'b', label = 'Berr')
plt.grid(True)
plt.title("Q11: Variation of error with noise in logarithmic scale")
plt.xlabel("$Noise\ Standard\ Deviation\\rightarrow$", size = 15)
plt.ylabel("$Mean\ Squared\ Error\\rightarrow$", size = 15)
plt.legend()
plt.stem(sig,Errors[:, 0], 'ro');
plt.stem(sig,Errors[:, 1], 'b');
plt.show()

print("Error Analysis has been completed.")