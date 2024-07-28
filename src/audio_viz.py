import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters
CHUNK = 1000  # Number of audio samples per frame
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sampling rate (samples per second)
AMPLIFICATION_FACTOR = 0.8  # Initial amplification factor for the entire signal
BASS_AMPLIFICATION_FACTOR = 2  # Initial amplification factor for the bass frequencies
BASS_MIN_FREQ = 20  # Minimum frequency for bass (in Hz)
BASS_MAX_FREQ = 500  # Maximum frequency for bass (in Hz)
PHASE_SHIFT_DEGREES = 0  # Phase shift for the overall signal in degrees
BASS_PHASE_SHIFT_DEGREES = 0  # Phase shift for the bass frequencies in degrees

# Convert degrees to radians
PHASE_SHIFT = np.deg2rad(PHASE_SHIFT_DEGREES)
BASS_PHASE_SHIFT = np.deg2rad(BASS_PHASE_SHIFT_DEGREES)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Initialize plot
fig, ax = plt.subplots()
x = np.arange(0, CHUNK)
line1, = ax.plot(x, np.random.rand(CHUNK), lw=2, label='Amplified Signal')
line2, = ax.plot(x, np.random.rand(CHUNK), lw=2, color='red', label='Amplified Bass Frequencies')

# Set up plot limits and labels
ax.set_ylim(-1, 1)
ax.set_xlim(0, CHUNK)
plt.ylabel('Amplitude')
plt.xlabel('Sample Index')
plt.legend()

# Function to apply phase shift
def apply_phase_shift(data, phase_shift):
    return data * np.cos(phase_shift) - np.imag(data) * np.sin(phase_shift)

# Function to update plot
def update(frame):
    # Read audio data from stream
    try:
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        
        # Normalize and amplify the signal
        normalized_data = data / (2**15)
        amplified_data = normalized_data * AMPLIFICATION_FACTOR
        
        # Apply phase shift to the amplified signal
        amplified_data = apply_phase_shift(amplified_data, PHASE_SHIFT)
        
        # Perform FFT
        fft_data = np.fft.fft(normalized_data)
        freqs = np.fft.fftfreq(len(fft_data), 1/RATE)
        
        # Isolate and amplify bass frequencies
        bass_fft_data = np.zeros_like(fft_data)
        for i, freq in enumerate(freqs):
            if BASS_MIN_FREQ <= abs(freq) <= BASS_MAX_FREQ:
                bass_fft_data[i] = fft_data[i]
        
        # Perform inverse FFT to get the bass signal in time domain
        bass_signal = np.fft.ifft(bass_fft_data).real * BASS_AMPLIFICATION_FACTOR

        # Apply phase shift to the bass signal
        bass_signal = apply_phase_shift(bass_signal, BASS_PHASE_SHIFT)

        # Update line data
        line1.set_ydata(amplified_data)
        line2.set_ydata(bass_signal)
        
    except IOError:
        print("Input overflowed!")

    return line1, line2

# Animation
ani = FuncAnimation(fig, update, interval=20, blit=True)

# Show plot
plt.show()

# Stop and close the stream when plot window is closed
stream.stop_stream()
stream.close()
p.terminate()