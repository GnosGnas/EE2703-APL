'''
Title    : Assignment-9
Purpose  : To extract spectra of non-periodic signals
Author   : Surya Prasad.S(EE19B121) 
Date     : 22nd May 2021
Outputs  : Magnitude and phase plots of DFT with and without using corrective techniques
'''


# Importing libraries
from pylab import *


# Function to analyse give signal's DFT
def plot_FFT(func, TITLE, r = [-pi, pi], N = 64, xlimit = 10, odd_signal = False, indB = False, estimate_flag = False):
    ## Time vector is being declared. Here we remove the last point because it will overlap with the initial point
    t = linspace(r[0], r[1], N + 1)[:-1]

    ## Frequency vector is being declared. temp is a just a temporary variable for the purpose of calculation
    temp = N * (pi/(r[1] - r[0]))
    w = linspace(-temp, temp, N + 1)[:-1]

    ## Computing functional values in the time domain and frequency domain
    ### For odd signals we make y[0] as 0 to reduce the error
    y = func(t)

    if odd_signal:
        y[0] = 0

    Y = fftshift(fft(fftshift(y)))/float(N)

    ## Plotting phase and magnitude plots for DFT of the signals
    figure()

    if indB:
        subplot(2, 1, 1)
        title("Frequency Spectrum of " + TITLE)
        semilogx(w, 20 * log10(abs(Y)), lw = 2)
        xlim([1, 10])
        ylim([-20, 0])
        ylabel(r"$|Y|$ (in dB)", size = 16)
        grid(True)

    else:
        subplot(2, 1, 1)
        title("Frequency Spectrum of " + TITLE)
        plot(w, abs(Y), lw = 2)
        xlim([-xlimit, xlimit])
        ylabel(r"$|Y|$", size = 16)
        grid(True)

    subplot(2, 1, 2)
    ii = where(abs(Y) > 1e-3)
    scatter(w, angle(Y), marker = 'o', color = '#D9D9D9')
    plot(w[ii], angle(Y[ii]), 'go', lw = 2)
    xlim([-xlimit, xlimit])
    ylabel(r"$\angle$$Y$ (in rad)", size = 16)
    xlabel(r"$\omega$ (in rad/s)", size = 16)
    grid(True)

    show()

    if estimate_flag:
    	return w, abs(Y), angle(Y)


# Question 1

## Function definition for root2 frequency
def sinroot2(x):
    return sin(sqrt(2) * x)

## Passing function definitions for DFT Analysis
plot_FFT(sinroot2, "$sin(\\sqrt{2}t)$", odd_signal = True)

## Plotting the given signal and its periodic approximation
x1 = linspace(-10, 10, 200)
x2 = linspace(-pi, pi, 100)
y1 = sinroot2(x1)
y2 = sinroot2(x2)

subplot(2, 1, 1)
title("Sampled interval of $sin(\\sqrt{2}t)$")
plot(x1, y1, label = 'Entire signal', color = '#002FA7')
plot(x2, y2, label = 'Sampled Interval', color = 'orange')
grid(True)
legend()

x3 = linspace(pi, 3 * pi, 100)
x4 = linspace(-3 * pi, -pi, 100)

subplot(2, 1, 2)
title("Periodic function approximation for $sin(\\sqrt{2}t)$")
plot(x2, y2, color = 'orange')
plot(x3, y2, color = '#002FA7')
plot(x4, y2, color = '#002FA7')
xlabel("t (in s)", size = 16)
grid(True)

show()

## Function definition for ramp function
def ramp(x):
    return x

## Passing function definitions for DFT Analysis
plot_FFT(ramp, "ramp function", odd_signal = True, indB = True)

## Function to return Hamming Window sequence
def HammingWindow(a, b, n):
    return fftshift(a + b * cos((2 * pi * n)/(len(n) - 1)))

## Function definition for root2 frequency with Windowing
def sinroot2_hamming(x):
    return sinroot2(x) * HammingWindow(0.54, 0.46, arange(len(x)))

## Plotting sinusoid for root2 frequency with Windowing
x2 = linspace(-pi, pi, 65)[:-1]
x3 = linspace(pi, 3 * pi, 65)[:-1]
x4 = linspace(-3 * pi, -pi, 65)[:-1]

y = sinroot2_hamming(x2)

title("Periodic plot of $sin(\\sqrt{2}t)$ with Windowing")
plot(x2, y, color = '#002FA7')
plot(x3, y, color = '#002FA7')
plot(x4, y, color = '#002FA7')
xlabel("$t$ (in s)", size = 16)
ylabel("$sin(\\sqrt{2}t)$", size = 16)
grid(True)
show()

## Passing function definitions for DFT Analysis
plot_FFT(sinroot2_hamming, "$sin(\\sqrt{2}t)$", xlimit = 8, odd_signal = True)

plot_FFT(sinroot2_hamming, "$sin(\\sqrt{2}t)$ with higher resolution", r = [-4 * pi, 4 * pi], xlimit = 4, N = 256, odd_signal = True)

## Analysing sin(1.25t) with the same procedure
### Function definition for sin(1.25t)
def sin_test(x):
    return sin(1.25 * x)

### Function definition for sin(1.25t) with windowing
def sin_test_hamming(x):
    return sin_test(x) * HammingWindow(0.54, 0.46, arange(len(x)))

### Passing function definitions for DFT Analysis
plot_FFT(sin_test, "$sin(1.25t)$", r = [-4 * pi, 4 * pi], xlimit = 4, odd_signal = True)

plot_FFT(sin_test_hamming, "$sin(1.25t)$ with Windowing", r = [-4 * pi, 4 * pi], xlimit = 4, odd_signal = True)


# Question 2

## Function definition for cos^3(0.86t)
def cubic_cos(x):
    return (cos(0.86 * x))**3

def cubic_cos_hamming(x):
    return cubic_cos(x) * HammingWindow(0.54, 0.46, arange(len(x)))

## Passing function definitions for DFT Analysis
plot_FFT(cubic_cos, "$cos^{3}(0.86t)$ without Windowing", r = [-4 * pi, 4 * pi], N = 512)

plot_FFT(cubic_cos_hamming, "$cos^{3}(0.86t)$ with Windowing", r = [-4 * pi, 4 * pi], N = 512)


# Question 3

## Function definition for cos(0.6t+1)
def cos_delta(x):
    return cos(0.6 * x + 1)

## Function definition for cos(0.6t+1) with Windowing
def cos_delta_hamming(x):
    return cos_delta(x) * HammingWindow(0.54, 0.46, arange(len(x)))

## Function to estimate w0 and delta
def estimate(w, mag, phase):
    actual_mag = where(mag > 0.2)

    w_avg = sum((mag[actual_mag]**2) * abs(w[actual_mag]))/sum(mag[actual_mag]**2)

    phase_avg = mean(abs(phase[actual_mag]))

    print("Estimated w0:", w_avg)
    print("Estimated delta:", phase_avg)

## Passing function definitions for DFT Analysis
w, mag, phase = plot_FFT(cos_delta, "$cos(0.6t+1)$ without Windowing", r = [-4 * pi, 4 * pi], xlimit = 4, N = 512, estimate_flag = True)
print("\nEstimations for cos(0.6t+1):")
estimate(w, mag, phase)

w, mag, phase = plot_FFT(cos_delta_hamming, "$cos(0.6t+1)$ with Windowing", r = [-4 * pi, 4 * pi], xlimit = 4, N = 512, estimate_flag = True)
print("\nEstimations for cos(0.6t+1)w(t):")
estimate(w, mag, phase)


# Question 4

## Function definition for cos(1.6t+1) with white gaussian noise
def cos_delta_with_noise(x):
    return cos(0.6 * x + 1) + 0.1 * randn(len(x))

## Function definition for cos(1.6t+1) with white gaussian noise with Windowing
def cos_delta_with_noise_hamming(x):
    return cos_delta_with_noise(x) * HammingWindow(0.54, 0.46, arange(len(x)))

## Passing function definitions for DFT Analysis
w, mag, phase = plot_FFT(cos_delta_with_noise, "noisy $cos(0.6t+1)$ without Windowing", r = [-4 * pi, 4 * pi], xlimit = 4, N = 512, estimate_flag = True)
print("\nEstimations for noisy cos(0.6t+1):")
estimate(w, mag, phase)

w, mag, phase = plot_FFT(cos_delta_with_noise_hamming, "noisy $cos(0.6t+1)$ with Windowing", r = [-4 * pi, 4 * pi], xlimit = 4, N = 512, estimate_flag = True)
print("\nEstimations for noisy cos(0.6t+1)w(t):")
estimate(w, mag, phase)


# Question 5

## Function definition for chirp function
def chirp(x):
    return cos(16 * x * (1.5 + x/(2 * pi)))

## Function definition for chirp function with Windowing
def chirp_hamming(x):
    return chirp(x) * HammingWindow(0.54, 0.46, arange(len(x)))

## Plotting chirped signal
x2 = linspace(-pi, pi, 1000)[:-1]
x3 = linspace(pi, 3 * pi, 1000)[:-1]
x4 = linspace(-3 * pi, -pi, 1000)[:-1]

y = chirp(x2)

title("Plot of chirped signal ($cos(16t(1.5+t/2\\pi))$)")
plot(x2, y, color = 'orange')
plot(x3, y, color = '#002FA7')
plot(x4, y, color = '#002FA7')
xlabel("$t$ (in s)", size = 16)
ylabel("$cos(16t(1.5+t/2\\pi))$", size = 16)
grid(True)
show()

y = chirp_hamming(x2)

title("Plot of chirped signal with Windowing")
plot(x2, y, color = 'orange')
plot(x3, y, color = '#002FA7')
plot(x4, y, color = '#002FA7')
xlabel("$t$ (in s)", size = 16)
ylabel("$cos(16t(1.5+t/2\\pi))w(t)$", size = 16)
grid(True)
show()

## Passing function definitions for DFT Analysis
plot_FFT(chirp, "chirp function without Windowing", xlimit = 100, N = 1024)

plot_FFT(chirp_hamming, "chirp function with Windowing", xlimit = 100, N = 1024)


# Question 6

## Defining time and frequency variables
t_full = linspace(-pi, pi, 1025)[:-1]

t_broken = reshape(t_full, (16, 64))

mags = []
phases = []

w = linspace(-512, 512, 65)[:-1]

## For loop to compute DFT for different ranges of time
for t in t_broken:
    y = chirp(t)
    y[0] = 0
    y = fftshift(y)
    Y = fftshift(fft(y))/64

    mags.append(abs(Y))
    phases.append(angle(Y))

mags = array(mags)
phases = array(phases)

X = w
Y = linspace(-pi, pi, 17)[:-1]

X, Y = meshgrid(X, Y)

## Plotting 3d plot of Frequency response vs frequency and time
fig = figure(1)

ax = fig.add_subplot(221, projection = "3d")
surf = ax.plot_surface(X, Y, mags, cmap = cm.plasma)
fig.colorbar(surf, shrink = 0.5)
ax.set_title("Surface plot of Magnitude Response vs Frequency and Time")
ax.set_xlabel("$\\omega$ (in rad/s)") 
ax.set_ylabel("$t$ (in s)")

ax = fig.add_subplot(211, projection = '3d')
surf = ax.plot_surface(X, Y, phases, cmap = cm.coolwarm_r)
fig.colorbar(surf, shrink = 0.5)
ax.set_title("Surface plot of Phase Response vs Frequency and Time")
ax.set_xlabel("$\\omega$ (in rad/s)") 
ax.set_ylabel("$t$ (in s)")
ax.set_zlabel("Phase of Y (in rad)")

show()



mags = []
phases = []

w = linspace(-512, 512, 65)[:-1]

## For loop to compute DFT for different ranges of time
for t in t_broken:
    y = chirp_hamming(t)
    y[0] = 0
    y = fftshift(y)
    Y = fftshift(fft(y))/64

    mags.append(abs(Y))
    phases.append(angle(Y))

mags = array(mags)
phases = array(phases)

X = w
Y = linspace(-pi, pi, 17)[:-1]

X, Y = meshgrid(X, Y)

## Plotting 3d plot of Frequency response vs frequency and time
fig = figure(1)

ax = fig.add_subplot(221, projection = "3d")
surf = ax.plot_surface(X, Y, mags, cmap = cm.plasma)
fig.colorbar(surf, shrink = 0.5)
ax.set_title("Surface plot of Magnitude Response vs Frequency and Time")
ax.set_xlabel("$\\omega$ (in rad/s)") 
ax.set_ylabel("$t$ (in s)")

ax = fig.add_subplot(211, projection = '3d')
surf = ax.plot_surface(X, Y, phases, cmap = cm.coolwarm_r)
fig.colorbar(surf, shrink = 0.5)
ax.set_title("Surface plot of Phase Response vs Frequency and Time")
ax.set_xlabel("$\\omega$ (in rad/s)") 
ax.set_ylabel("$t$ (in s)")
ax.set_zlabel("Phase of Y (in rad)")

show()