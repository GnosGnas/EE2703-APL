'''
Title    : Assignment-8
Purpose  : To analyse Digital Fourier Transforms of periodic signals
Author   : Surya Prasad.S(EE19B121) 
Date     : 24th April 2021
Outputs  : Magnitude and phase plot of DFT of the signals
'''


# Importing libraries
import sys
from pylab import *


# Default value for number of samples
N = 2048

# Checking for valid commandline arguments
## The user can at max put one value
if len(sys.argv) > 2:
    print("Too many arguments passed in commandline. Maximum of 1 argument can only be passed.")
    exit()

elif len(sys.argv) == 2:
    N = int(sys.argv[1])

if N < 0:
    print("Invalid parameter passed. Only positive value is expected.")
    exit()


# Function to analyse given signal's DFT
## The inputs to this function are the function definition, Title to be given to the plot, the range of time and the endpoints of the x axis
def plot_analysis(func, TITLE, r, xlimit = 10):
    ## Time vector is being declared. Here we remove the last point because it will overlap with the initial point
    t = linspace(r[0], r[1], N + 1)
    t = t[:-1]

    ## Frequency vector is being declared. temp is a just a temporary variable for the purpose of calculation
    temp = N * (pi/(r[1] - r[0]))
    w = linspace(-temp, temp, N + 1)
    w = w[:-1]

    ## Computing functional values in the time domain and frequency domain
    ### For normal functions we shall be passing the function definition and for gaussian alone we shall just pass the string
    if func == 'Gauss':
        y = exp(-t**2/2)
        Y = fftshift(abs(fft(y)))/float(N)

        ### Normalizing for the case of gaussian
        Y = Y * sqrt(2 * pi)/max(Y)
        Y_ = exp(-w**2/2) * sqrt(2 * pi)
        print("Max error for time range as [{}π, {}π) is {}".format(round(r[0]/pi), round(r[1]/pi), abs(Y - Y_).max()))

    else:
        y = func(t)
        Y = fftshift(fft(y))/float(N)

    ## Plotting phase and magnitude plots for DFT of the signals
    figure()

    subplot(2, 1, 1)
    title(TITLE)
    plot(w, abs(Y), lw = 2)
    xlim([-xlimit, xlimit])
    ylabel(r"Magnitude Response ($|y|$)", size = 16)
    grid(True)

    subplot(2, 1, 2)
    ii = where(abs(Y) > 1e-3)
    scatter(w, angle(Y), marker = 'o', color = '#D9D9D9')
    plot(w[ii], angle(Y[ii]), 'go', lw = 2)
    xlim([-xlimit, xlimit])
    ylabel(r"Phase Response ($\angle$$Y$)", size = 16)
    xlabel(r"$k$", size = 16)
    grid(True)

    show()


# Functions to pass as input to plot_analysis()

## Function definition for sin(5t)
def func_sin5(x):
    return sin(5 * x)

## Function definition for Amplitude Modulated signal
def func_AM(x):
    return cos(10 * x) * (1 + 0.1 * cos(x))

## Function definition for (sin(x))^3
def func1(x):
    return (sin(x))**3

## Function definition for (cos(x))^3
def func2(x):
    return (cos(x))**3

## Function definition for Frequency Modulated Signal
def func3(x):
    return cos(20 * x + 5 * cos(x))


# Passing function definitions for DFT Analysis

## 1. Passing sin(5t)
plot_analysis(func_sin5, r"Spectrum of $sin(5t)$", [0, 2 * pi])

## 2. Passing Amplitude Modulated signal at low and high sampling frequency
plot_analysis(func_AM, r"Spectrum of $(1+0.1cos(t))cos(10t)$ at low sampling frequency", [0, 2 * pi], xlimit = 15)

plot_analysis(func_AM, r"Spectrum of $(1+0.1cos(t))cos(10t)$ at higher sampling frequency", [-4 * pi, 4 * pi], xlimit = 15)

## 3. Passing (sin(x))^3
plot_analysis(func1, r"Spectrum of $sin^3(t)$", [-4 * pi, 4 * pi])

## 4. Passing (cos(x))^3
plot_analysis(func2, r"Spectrum of $cos^3(t)$", [-4 * pi, 4 * pi])

## 5. Passing Frequency Modulated Signal
plot_analysis(func3, r"Spectrum of $cos(20t+5cos(t))$", [-4 * pi, 4 * pi], xlimit = 40)

## 6. Gaussian function
### Here we pass only the string and identify the ideal sampling rate
for i in range(1, 11):
    plot_analysis("Gauss", r"Spectrum of Gaussian $\exp(-t^2/2)$ for time range: [-" + str(i) + r"π, " + str(i) + r"π]", [-i * pi, i * pi])
