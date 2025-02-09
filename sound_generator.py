import pygame
import numpy as np
import wave
import struct
import os

# Sample rate explanation:
# 44100 Hz (samples per second) is the CD-quality audio standard
# Chosen because:
# 1. Human hearing range is 20 Hz to 20 kHz
# 2. Nyquist theorem requires sampling at 2x the highest frequency (40 kHz)
# 3. 44.1 kHz gives a small buffer above the minimum required rate
SAMPLE_RATE = 44100

# Initialize pygame mixer with our sample rate
# -16 means 16-bit signed audio
# 1 means mono audio
# 512 is the buffer size
pygame.mixer.init(SAMPLE_RATE, -16, 1, 512)

def create_sound_directory():
    """Create directory for storing generated sound files."""
    if not os.path.exists('sounds'):
        os.makedirs('sounds')

def save_sound(name, samples):
    """Save generated sound samples as a WAV file.
    
    Args:
        name: Output filename (without .wav extension)
        samples: Array of float values between -1.0 and 1.0
    
    Technical details:
    - Uses 16-bit signed integers (struct format 'h')
    - Scales float samples to full 16-bit range (-32767 to +32767)
    - Uses system's native byte order (little-endian on most systems)
    
    Note on endianness:
    - Terms come from Gulliver's Travels (1726), where two groups fought over which end to break eggs:
      'Little-Endians' (little end) vs 'Big-Endians' (big end). Computer scientist Danny Cohen
      borrowed these terms in 1981 to describe byte order.
    - Little-endian stores least significant byte first (like starting arithmetic from ones digit)
    - Big-endian stores most significant byte first (like reading numbers left-to-right)
    - Most modern CPUs (including Intel/AMD) use little-endian for efficient arithmetic
    """
    with wave.open(f'sounds/{name}.wav', 'w') as wav_file:
        # WAV file parameters
        nchannels = 1  # Mono audio
        sampwidth = 2  # 2 bytes per sample (16-bit)
        framerate = SAMPLE_RATE
        nframes = len(samples)
        
        # Set wav file parameters
        wav_file.setparams((nchannels, sampwidth, framerate, nframes, 'NONE', 'not compressed'))
        
        # Write each sample as a 16-bit integer
        for sample in samples:
            # Convert float (-1.0 to +1.0) to 16-bit int (-32767 to +32767)
            # struct.pack('h', ...) creates a 2-byte string in native byte order
            packed_value = struct.pack('h', int(sample * 32767.0))
            wav_file.writeframes(packed_value)

def generate_shoot_sound():
    """Generate a shooting sound effect.
    Creates a descending pitch (1000Hz to 500Hz) with exponential decay.
    Duration: 0.1 seconds (4,410 samples at 44.1kHz)"""
    duration = 0.1  # seconds
    # Create time array with SAMPLE_RATE points per second
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    # Create descending frequency array
    frequency = np.linspace(1000, 500, len(t))  # Descending pitch
    # Generate sine wave and apply exponential decay envelope
    samples = np.sin(2 * np.pi * frequency * t) * np.exp(-5 * t)
    return samples

def generate_explosion_sound():
    """Generate an explosion sound effect.
    Uses random noise with fast exponential decay for a 'boom' effect.
    Duration: 0.3 seconds (13,230 samples at 44.1kHz)"""
    duration = 0.3  # seconds
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    # Random noise creates rich frequency content
    noise = np.random.uniform(-1, 1, len(t))
    # Faster decay (-8) for sharp explosion sound
    envelope = np.exp(-8 * t)
    samples = noise * envelope
    return samples

def generate_ufo_sound():
    """Generate a UFO sound effect.
    Combines two close frequencies (180Hz and 200Hz) to create a beating effect.
    Duration: 1.0 seconds (44,100 samples at 44.1kHz)"""
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    # Two close frequencies create a 'wobble' effect
    freq1, freq2 = 180, 200
    samples = 0.5 * (np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t))
    return samples

def generate_game_over_sound():
    """Generate a game over sound effect.
    Creates a slow descending pitch (400Hz to 200Hz) with slow decay.
    Duration: 1.0 seconds (44,100 samples at 44.1kHz)"""
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    frequency = np.linspace(400, 200, len(t))  # Descending pitch
    # Slower decay (-2) for longer lasting sound
    samples = np.sin(2 * np.pi * frequency * t) * np.exp(-2 * t)
    return samples

def main():
    """Generate all sound effects for the Space Invaders game.
    
    Creates four distinct sound effects:
    1. Shooting sound: Short descending pitch (0.1s)
    2. Explosion sound: White noise with sharp decay (0.3s)
    3. UFO sound: Beating effect from two frequencies (1.0s)
    4. Game over sound: Long descending pitch (1.0s)
    
    All sounds are generated at 44.1kHz sample rate and saved as 16-bit WAV files.
    """
    create_sound_directory()
    
    # Dictionary mapping sound names to their generated samples
    sounds = {
        'shoot': generate_shoot_sound(),
        'explosion': generate_explosion_sound(),
        'ufo': generate_ufo_sound(),
        'game_over': generate_game_over_sound()
    }
    
    # Save each sound as a WAV file
    for name, samples in sounds.items():
        save_sound(name, samples)
        print(f"Generated {name}.wav")

if __name__ == '__main__':
    main()
