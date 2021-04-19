'''
Title    : Assignment-6
Purpose  : To simulate a tube light
Author   : Surya Prasad.S(EE19B121) 
Date     : 11th April 2021
Inputs   : A maximum of 6 parameters can be given as input
Outputs  : Plots of Electron Density Histogram, Light Intensity Histogram and Electron Phase Space along with the results of Intensity in a tabulated column.
'''


# Importing libraries
import sys
from pylab import *


# Default values are assigned to parameters
n = 100                     # Spatial grid size
M = 5                       # Number of electrons injected per turn
nk = 500                    # Number of turns to simulate
u0 = 5                      # Threshold velocity
p = 0.25                    # Probability that ionisation will occur
Msig = 2                    # Deviation of electrons injected per turn


# Checking for valid commandline arguments

## The user has the option to pass values for all 6 parameters or just for the first few
if len(sys.argv) > 7:
    print("Too many arguments passed in commandline. Maximum of 6 arguments can only be passed.")
    exit()

else:
    for i in range(len(sys.argv)):
        if i == 1:
            n = int(sys.argv[1])
        
        elif i == 2:
            M = int(sys.argv[2])
        
        elif i == 3:
            nk = int(sys.argv[3])
        
        elif i == 4:
            u0 = int(sys.argv[4])

        elif i == 5:
            p = float(sys.argv[5])
        
        elif i == 6:
            Msig = int(sys.argv[6])


## Checking for valid values
if n < 0 or M < 0 or nk < 0 or u0 < 0 or p < 0 or p >1 or Msig < 1 or Msig > M:
    print("Invalid parameters passed. Please try again.") 


# Variables to hold electron information
xx = zeros(n * M)           # Electron position
u = zeros(n * M)            # Electron velocity
dx = zeros(n * M)           # Displacement in current turn


# Variables to hold information for simulation
## In each turn, we record this information and since we don't know its length we are storing them as lists and extending them as required.
I = []                      # Intensity of emitted light
X = []                      # Electron position
V = []                      # Electron velocity


# Initialising ii (indices where position is more than 0) and all_ii (all indices)
ii = where(xx > 0)[0]
all_ii = set(list(range(n*M)))


# For loop to perform simulation
for i in range(nk):
    ## First we take all those electrons whose position is greater than 0
    ### These will get accelerated at 1 ms^-2
    dx[ii] = u[ii] + 0.5
    xx[ii] += dx[ii]
    u[ii] += 1


    ## We are checking if any of the electrons reached the anode and if yes then appropriately changes are made
    reached_end = where(xx[ii] > n)[0]
    xx[ii[reached_end]] = 0
    u[ii[reached_end]] = 0
    dx[ii[reached_end]] = 0


    ## Checking if any of the electrons achieved more than threshold speed
    ### For these electrons some of them collide based on probability p and their velocties become 0
    kk = where(u >= u0)[0]
    ll = where(rand(len(kk)) <= p)[0]
    kl = kk[ll]
    u[kl] = 0

    ### Determining colision points
    rho = rand(len(kl))
    xx[kl] -= (dx[kl] * rho)

    ### Adding the position of the excited atoms to I vector
    I.extend(xx[kl].tolist())


    ## Injecting new electrons
    ### Here we give the position as 1 for the injected electrons
    m = int(randn() * Msig + M)

    not_ii = where(xx == 0)                 # Indices where position is 0
    free_slots = min(len(not_ii), m)        # Number of free slots in which electrons got injected
    xx[not_ii[:free_slots]] = 1
    u[not_ii[:free_slots]] = 0
    dx[not_ii[:free_slots]] = 0
    

    ## Reusing not_ii to generate ii
    ii = array(list(all_ii - set(not_ii[0])), dtype=int)
    

    ## Adding the information to the appropriate vectors
    X.extend(xx.tolist())
    V.extend(u.tolist())

'''
# Plotting Electron Density Histogram
plt.figure(0)
plt.hist(X, bins = arange(0, 101, 1), rwidth = 0.8, color = 'purple')
plt.title('Electron Density Histogram')
plt.xlabel('Position$\\rightarrow$')
plt.ylabel('Number of electrons$\\rightarrow$')
plt.show()
'''

# Plotting Light Intensity Histogram
plt.figure(1)
population,bins,_ = plt.hist(I, bins = arange(0, 101, 1), rwidth = 1.5, color = 'white', ec = 'blue')
plt.title('Light Intensity Histogram (' + str(u0) + ", " + str(p) + ")")
plt.xlabel('Position$\\rightarrow$')
ylabel('Intensity$\\rightarrow$')
plt.show()

'''
# Plotting Electron Phase Space
plt.figure(2)
plt.plot(X, V, 'bo', markersize = 4)
plt.title("Electron Phase Space")
plt.xlabel('Position$\\rightarrow$')
plt.ylabel('Velocity of electron$\\rightarrow$')
plt.show()
'''

# Tabulating results
## Since bins go over a range of values we shall consider only the middle of each bin
xpos = 0.5*(bins[0:-1] + bins[1:])
'''
## Printing the results
print("Intensity data:\nxpos\tcount")

for i in range(len(bins) - 1):
    print(" ", xpos[i],"\t ",int(population[i]),sep="")
'''