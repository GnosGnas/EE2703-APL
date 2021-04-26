'''
Title    : Assignment-7
Purpose  : To analyse LTI systems with Sympy in Python
Author   : Surya Prasad.S(EE19B121) 
Date     : 24th April 2021
Outputs  : Magnitude Plot, Step response and output response against given input signals for each filters are shown
'''


# Importing libraries
import scipy.signal as sp
import pylab as p
import sympy as sy
from sympy.abc import s,t


# Function to extract coefficients from symbolic representation of a transfer function and returns LTI class
def sym_to_sys(sym):
    ## First we shall split the symbolic representation into its numerator and denominator
    n, d = sy.fraction(sym)

    ## Then we shall extract the polynomial terms from it
    n, d = sy.Poly(n, s), sy.Poly(d, s)

    ## Now we can store the coefficients of the terms and then check if the given system can be solved.
    ### If valid, then they are used to make the LTI type class
    num, den = n.all_coeffs(), d.all_coeffs()

    if len(num) > len(den):
        print("Invalid system passed.")
        exit()

    H = sp.lti(p.array(num, dtype = float), p.array(den, dtype = float))
    return H


# Function to plot Magnitude Response (Bode plot)
def bode_analysis(H, title):
    w = p.logspace(0, 12, 1001)
    ss = 1j * w
    hf = sy.lambdify(s, H, 'numpy')
    h = hf(ss)

    ## Plotting in loglog scale (Bode plot)
    p.figure(0)
    p.loglog(w, abs(h), lw=2)
    p.title("Bode plot of the " + title)
    p.xlabel("Frequency (in rad/s)$\\rightarrow$")
    p.ylabel("Magnitude (in log scale)$\\rightarrow$")
    p.grid(True)
    p.show()


# Function to plot response for a given input signal
def input_sim(H, Vi, t_range, title, type):
    x = sp.lsim(H, Vi, t_range)[1]
    p.plot(t_range, Vi, label = 'Input signal')
    p.plot(t_range, x, label = 'Output response')
    p.title(title + " input signal vs output response of " + type)
    p.xlabel("time (in s)$\\rightarrow$")
    p.ylabel("Voltage (in V)$\\rightarrow$")
    p.legend()
    p.grid(True)
    p.show()
    

# Common function to analyse given input signal and transfer function
def plot_analysis(H, Vi, t_range, title):
    H_lti = sym_to_sys(H)
    bode_analysis(H, title)

    ## Computing and plotting step response
    step_response = H * 1/s
    step_response_lti = sym_to_sys(step_response)
    x = sp.impulse(step_response_lti, None, t_range)[1]
    p.figure(1)
    p.plot(t_range, x)
    p.title("Step Response of the " + title)
    p.xlabel("time (in s)$\\rightarrow$")
    p.ylabel("Response (in V)$\\rightarrow$")
    p.grid(True)
    p.show()

    ## Response to a damped low frequency signal
    p.figure(2)
    V_low_freq = p.exp(-300 * t_range) * p.cos(2 * 10**3 * p.pi * t_range)
    input_sim(H_lti, V_low_freq, t_range, "Low frequency (1KHz)", title)

    ## Response to a damped high frequency signal
    p.figure(3)
    V_high_freq = p.exp(-300 * t_range) * p.cos(2 * 10**6 * p.pi * t_range)
    input_sim(H_lti, V_high_freq, t_range, "High frequency (1MHz)", title)

    ## Response to the given input signal
    p.figure(4)
    input_sim(H_lti, Vi, t_range, "Given", title)


# Analysis for Lowpass Filter

## Function to compute and return the symbolic representation of the matrices and the transfer function
def lowpass_tf(R1, R2, C1, C2, G):
    A = sy.Matrix([[0, 0, 1, -1/G],\
            [-1/(1 + s * R2 * C2), 1, 0, 0],\
            [0, -G, G, 1],\
            [-1/R1 - 1/R2 - s * C1, 1/R2, 0, s * C1]])
    b =  sy.Matrix([0, 0, 0, -1/R1])
    V = A.inv() * b
    return A, b, V

## Defining the time range for plotting purpose
t = p.linspace(0, 1e-2, 1000000)

## Passing values to compute the transfer function
A, b, V = lowpass_tf(10000, 10000, 1e-9, 1e-9, 1.586)
Vo = V[3]

## Vi is the input which is given to the filter
Vi = p.sin(2000 * p.pi * t) + p.cos(2 * 10**6 * p.pi * t)

# Approximate behaviour at high frequencies
Vo_exp = 1/(1 + s * 1e4 * 1e-9)
bode_analysis(Vo_exp, "approximated Lowpass Filter")

## Passing for plot analysis
plot_analysis(Vo, Vi, t, "Lowpass Filter")


# Analysis for Highpass Filter

## Function to compute and return the symbolic representation of the matrices and the transfer function
def highpass_tf(R1, R3, C1, C2, G):
    A = sy.Matrix([[0, -1, 0, 1/G],
        [s * C2 * R3/(s * C2 * R3 + 1), 0, -1, 0],
        [0, G, -G, 1],
        [-s * C2 -1/R1 - s * C1, 0, s * C2, 1/R1]])

    b = sy.Matrix([0, 0, 0, -s * C1])
    V = A.inv() * b
    return A, b, V

## Defining the time range for plotting purpose
t = p.linspace(0, 1e-2, 1000000)

## Passing values to compute the transfer function
A, b, V = highpass_tf(1e4, 1e4, 1e-9, 1e-9, 1.586)
Vo = V[3]

## Vi is the input which is given to the filter
Vi = p.exp(-300 * t) *  (p.sin(2e6 * p.pi * t) + p.cos(2e3 * p.pi * t))

# Approximate behaviour at high frequencies
Vo_exp = (s * 1e4 * 1e-9)/(1 + s * 1e4 * 1e-9)
bode_analysis(Vo_exp, "approximated Highpass Filter")

## Passing for plot analysis
plot_analysis(Vo, Vi, t, "Highpass Filter")
