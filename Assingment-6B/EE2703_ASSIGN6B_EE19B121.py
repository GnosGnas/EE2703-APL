'''
Title    : Assignment-6B
Purpose  : To analyse LTI systems with numerical tools in Python
Author   : Surya Prasad.S(EE19B121) 
Date     : 18th April 2021
Outputs  : Plots of various signals
'''


# Importing libraries
import scipy.signal as sp
import pylab as p 


# Common function for Question 1 and 2 

## Function to plot the impulse response. Decay takes the value of the rate at which decay occurs
def func(decay):
    ### Frequency response of a spring is being calculated
    f_spring_num = p.poly1d([1, decay])
    f_den = p.poly1d([1, 2 * decay, 2.25 + decay**2])
    diff_coeff = p.poly1d([1, 0, 2.25])
    f_spring_den = p.polymul(f_den, diff_coeff)

    ### Converting the coefficients to LTI system type for generating impulse response
    f_lti = sp.lti(f_spring_num, f_spring_den)
    t, x = sp.impulse(f_lti, None, p.linspace(0, 50, 1000))
    
    ### Plotting the response
    p.plot(t, x)
    p.xlabel('time$\\rightarrow$')
    p.ylabel('x$\\rightarrow$')
    p.show()


# Question 1
## The rate of decay of the input is 0.5
p.figure(0)
p.title("1. Forced Damping Oscillator with decay=0.5")
func(0.5)


# Question 2
## The rate of decay of the input is 0.05
p.figure(1)
p.title("2. Forced Damping Oscillator with decay=0.05")
func(0.05)


# Question 3
freq = p.linspace(1.4, 1.6, 5)
H = sp.lti([1], [1, 0, 2.25])
t = p.linspace(0, 70, 500)

for i in freq:
    f_t = p.cos(i * t) * p.exp(-0.05 * t) * (t > 0)
    t, x, _ = sp.lsim(H, f_t, t)
    p.figure()
    p.title("3. Forced Damped Oscillator with frequency=" + str(i))
    p.xlabel('time$\\rightarrow$')
    p.ylabel('Output in time domain$\\rightarrow$')
    p.plot(t, x)

p.show()


# Question 4
## Coupled spring problem

### Computing the signals in time domain
X = sp.lti([1, 0, 2], [1, 0, 3, 0])
t, x = sp.impulse(X, None, p.linspace(0, 20, 5001))

Y = sp.lti([2], [1, 0, 3, 0])
t, y = sp.impulse(Y, None, p.linspace(0, 20, 5001))

### Plotting x(t)
p.figure(2)
p.title("4. Coupled spring problem")
p.xlabel('time$\\rightarrow$')
p.ylabel('Outputs')
p.plot(t, x, label = 'x(t)')
p.plot(t, y, label = 'y(t)')
p.legend()
p.show()


# Question 5
## The Transfer Function of the 2-port network is given as 1/( L*C*s**2 + R*C*s + 1)
H = sp.lti([1], [1e-12, 1e-4, 1])
w, S, phi = H.bode()

## Plotting the Magnitude and Phase response
fig, (ax1, ax2) = p.subplots(2, 1)
ax1.set_title("5. Magnitude Response")
ax1.semilogx(w, S)
ax2.set_title("5. Phase Response")
ax2.semilogx(w, phi)
p.show()


# Question 6
## First we shall find the output upto time 30µs
t = p.linspace(0, 30e-6, 500)
vi = p.cos(1e3 * t) - p.cos(1e6 * t)
t, x, _ = sp.lsim(H, vi, t)

## Plotting the output of the 2-port Network
p.figure(5)
p.title("6. Output response of the 2-port Network (t < 30µs)")
p.xlabel('time$\\rightarrow$')
p.ylabel('x(t)$\\rightarrow$')
p.plot(t, x)
p.show()

## First we shall find the output upto time 100ms
t = p.linspace(0, 10e-3, 100001)
vi = p.cos(1e3 * t) - p.cos(1e6 * t)
t, x, _ = sp.lsim(H, vi, t)

## Plotting the output of the 2-port Network
p.figure(6)
p.title("6. Output response of the 2-port Network (t < 10ms)")
p.xlabel('time$\\rightarrow$')
p.ylabel('x(t)$\\rightarrow$')
p.plot(t, x)
p.show()
