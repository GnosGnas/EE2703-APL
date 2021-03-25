'''
Title    : Assignment-5
Purpose  : To find flow of currents and visualise Temperature distribution over a conductor.
Author   : Surya Prasad.S(EE19B121) 
Date     : 25th March 2021
Inputs   : Inputs are optional and a maximum of 4 values can be passed
Outputs  : Various plots of Potential, currents and temperature and estimating the parameters to fit error in calculating Potentials.
'''


# Importing libraries
import numpy as np
import os, sys
import scipy.linalg as sp
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3


# Default values are assigned to parameters
Nx = 25                 # Number of x coordinates          
Ny = 25                 # Number of y coordinates
radius = 8              # Radius of wire portion
Niter = 1500            # Number of iterations


# Checking for valid commandline arguments.

## The user has the option to pass values for all 4 parameters or just for the first few.
if len(sys.argv) > 5:
    print("Too many arguments passed in commandline. Maximum of 4 arguments can only be passed.")
    exit()

else:
    for i in range(len(sys.argv)):
        if i == 1:
            Nx = int(sys.argv[1])

        elif i == 2:
            Ny = int(sys.argv[2])

        elif i == 3:
            radius = int(sys.argv[3])

        elif i == 4:
            Niter = int(sys.argv[4])

## Checking for positive values
if Nx < 0 or Ny < 0 or radius < 0 or Niter < 0:
    print("Invalid parameters passed. Please try again.")
    exit()

## Displaying the parameters
print("""The following are the parameters used for analysis:
    Number of nodes in each row =""", Nx,"""
    Number of nodes in each column =""", Ny,"""
    Radius of the cross-section =""", radius,"""
    Number of iterations =""", Niter,"""
    Size of conductor = 1cm X 1cm""")


# The radius is entered in units and is converted to centimeters.
## Here I have divided the radius by the harmonic mean of Nx and Ny. When Nx=Ny then radius = radius/Nx effectively.
radius = radius * (1/2) * ((1/Nx) + (1/Ny))

## Checking if the radius is bigger than 0.5 cm
if radius > 0.5:
    print("Given radius is too big. Please try again.")
    exit()


# Initialising Potentials as 0 and assigning the nodes in the wire portion to be 1V.
## ii represents all the coordinates satisfying the condition
phi = np.zeros((Ny, Nx), dtype = float)
x = np.linspace(-0.5, 0.5, num = Ny, dtype = float)
y = np.linspace(-0.5, 0.5, num = Nx, dtype = float)
Y, X = np.meshgrid(y, x)
ii = np.where(X**2 + Y**2 <= radius**2)
phi[ii] = 1.0


# Plotting the initial value of Potentials
plt.figure(1)
plt.title("Plot of Initial Potentials")
plt.xlabel("X coordinates")
plt.ylabel("Y coordinates")
plt.contourf(X, Y, phi, colors = ['#481b6d', 'blue', 'green', 'yellow', 'orange', 'red', 'white'])
plt.plot(x[ii[0]], y[ii[1]], 'ro')
plt.colorbar()
plt.show()


# Updating Potentials
## Here we iterate Niter times to calculate the final Potentials
## The difference is the calculations is stored in an array as errors
errors = np.zeros(Niter)

for k in range(Niter):
    oldphi = phi.copy()

    phi[1:-1, 1:-1] = 0.25 * (oldphi[1:-1, 0:-2] + oldphi[1:-1, 2:] + oldphi[0:-2, 1:-1] + oldphi[2:, 1:-1])

    phi[:, 0] = phi[:, 1]       
    phi[:, Nx-1] = phi[:, Nx-2]      
    phi[0, :] = phi[1, :] 
    phi[Ny-1, :] = 0
    phi[np.where(X**2 + Y**2 < radius**2)] = 1.0   

    errors[k] = np.max(np.abs(phi - oldphi))
    if(errors[k] == 0):
        break


# Plotting the errors got in calculating Potential in semilog and loglog scale
plt.figure(2)
plt.title("Plot of errors in semilog scale")
plt.xlabel("Number of iterations")
plt.ylabel("Errors")
plt.semilogy(np.asarray(range(Niter)), errors)
plt.semilogy((np.asarray(range(Niter)) + 1)[::50], errors[::50],'ro')
plt.legend(["All errors","every 50th value"])
plt.show()

plt.figure(3)
plt.title("Plot of errors in loglog scale")
plt.xlabel("Number of iterations")
plt.ylabel("Errors")
plt.loglog((np.asarray(range(Niter)) + 1), errors)
plt.loglog((np.asarray(range(Niter)) + 1)[::50], errors[::50],'ro')
plt.legend(["All errors","every 50th value"])
plt.show()


# Fitting the errors

## Here we shall define a function to fit the errors as an exponential curve using Least Squares Approach
def Log_Error_Fit(errors, start = 0):
    n_iter = errors.shape[0]
    log_errors = np.log(errors)
    return sp.lstsq(np.c_[np.ones((1, n_iter)).reshape(n_iter, 1), np.array(range(start, n_iter + start))], log_errors)[0]

## It is possible that there might be more errors when we take the error values from the 1st iteration so we identify the parameters for the entire vector and for errors after 500 iterations
A1, B1 = Log_Error_Fit(errors)
A2, B2 = Log_Error_Fit(errors[500:], 500)
K = np.array(range(Niter)) + 1

print("""\nIteration completed and errors have been fitted into an exponential plot of the form 'exp(A+B*x)'.
    Fitting based on all errors: exp({:.5} {:.5}*x)
    Fitting based on all errors after 500 iterations: exp({:.5} {:.5}*x)""".format(A1, B1, A2, B2), sep='')

## Plotting of the errors in semilog scale and loglog scale
plt.figure(4)
plt.title("Plot of actual errors vs fitted errors in semilog scale")
plt.xlabel("Number of iterations")
plt.ylabel("Errors")
plt.semilogy(K, errors)
plt.semilogy(K[::100], np.exp(A1 + B1 * (K-1))[::100], 'ro')
plt.semilogy(K[::100], np.exp(A2 + B2 * (K-1))[::100], 'go', markersize = 4)
plt.legend(["Actual errors","fit1","fit2"])
plt.show()

plt.figure(5)
plt.title("Plot of actual errors vs fitted errors in loglog scale")
plt.xlabel("Number of iterations")
plt.ylabel("Errors")
plt.loglog(K, errors)
plt.loglog(K[::100], np.exp(A1 + B1 * (K-1))[::100], 'ro')
plt.loglog(K[::100], np.exp(A2 + B2 * (K-1))[::100], 'go', markersize = 4)
plt.legend([" Actual errors", "fit1", "fit2"])
plt.show()


# Computing cumulative error

## We shall compute the sum of all the errors after Niter iterations so that we have an idea about how much error we might 
N_iterations = np.arange(200, 2001, 10)
Error_iteration = -(A1/B1) * np.exp(B1 * (N_iterations + 0.5))

## Plotting Cumulative error in loglog scale against number of iterations
plt.figure(6)
plt.title("Plot of Cumulative error in loglog scale")
plt.xlabel("Number of iterations")
plt.ylabel("Maximum error in computation")
plt.loglog(N_iterations, np.abs(Error_iteration), 'ro', markersize = 3)
plt.grid(True)
plt.show()


# Plotting plots of Final Potentials

## Plotting 3-D Surface Plot of Final Potential values
fig1 = plt.figure(7)
plt.title('3-D Surface Plot of Potentials')
ax = p3.Axes3D(fig1)
surf = ax.plot_surface(Y, X, phi, rstride=1, cstride=1, cmap=plt.cm.jet)
plt.show()

## Plotting 2-D Contour Plot of Final Potential values
plt.figure(8)
plt.title("2-D Contour Plot of Potentials")
plt.xlabel("X")
plt.ylabel("Y")
plt.plot(x[ii[0]], y[ii[1]],'ro')
plt.contourf(Y, X[::-1], phi, cmap='magma')
plt.colorbar()
plt.show()


# Computing current density distribution
Jx, Jy = 1/2 * (phi[1:-1, 0:-2] - phi[1:-1, 2:]), 1/2 * (phi[:-2, 1:-1] - phi[2:, 1:-1])


# Plotting of current density
plt.figure(9)
plt.title("Vector plot of current flow")
plt.quiver(Y[1:-1, 1:-1], -X[1:-1, 1:-1], -Jx[:, ::-1], -Jy, scale=6)
plt.plot(x[ii[0]], y[ii[1]],'ro')
plt.show()


# Computing and plotting Temperature distribution

## First we shall declare and initialise all values as 1
T = 300 * np.ones((Ny,Nx), dtype = float)

## For loop to compute Temperature
for k in range(Niter):
    oldT = T.copy()
    T[1:-1, 1:-1] = 0.25 * (oldT[1:-1, 0:-2] + oldT[1:-1, 2:] + oldT[0:-2, 1:-1] + oldT[2:, 1:-1] + (Jx)**2 + (Jy)**2)
    T[:, 0] = T[:, 1] 
    T[:, Nx-1] = T[:, Nx-2] 
    T[0, :] = T[1, :]
    T[Ny-1, :] = 300.0
    T[ii] = 300.0    

## Plotting 2-D Contour of Temperature distribution
plt.figure(10)
plt.title("2-D Contour plot of Temperature distribution")
plt.xlabel("X")
plt.ylabel("Y")
plt.contourf(Y, X[::-1], T, cmap='magma')
plt.colorbar()
plt.show()
