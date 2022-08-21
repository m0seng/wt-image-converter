import numpy as np
import scipy.fft

def wave2hsv(
    wave: np.ndarray,
    frame_size: int = 2048,
    limit_partials: bool = False,
    partial_cutoff: int = None,
    allow_incomplete: bool = True
) -> np.ndarray:
    
    IMAGE_MAX_VALUE = 256
    IMAGE_SATURATION = 255
    PHASE_OFFSET = 0
    TWO_PI = 2 * np.pi

    # handle incomplete frames
    frame_remainder = wave.shape[0] % frame_size
    if frame_remainder != 0:
        if allow_incomplete:
            # pad out last frame with zeros
            padding_length = frame_size - frame_remainder
            wave_padding = np.zeros(padding_length, dtype=wave.dtype)
            wave = np.hstack((wave, wave_padding))
        else:
            raise ValueError("Invalid wavetable: incomplete frame")
    frame_count = wave.shape[0] // frame_size

    # reshape into array of frames
    frames = wave.reshape((frame_count, frame_size))

    # FFT frames in parallel
    frames_fft: np.ndarray = scipy.fft.rfft(frames, axis=1)

    # limit partials
    if limit_partials and partial_cutoff < frames_fft.shape[1]:
        frames_fft = frames_fft[:,:partial_cutoff]
    fft_size = frames_fft.shape[1]

    # calculate magnitudes and phases
    magnitudes = np.absolute(frames_fft)
    phases = np.angle(frames_fft)

    # scale magnitudes by partial number
    magnitude_multipliers = np.arange(fft_size)
    magnitude_multipliers[0] = 1 # don't delete the DC offset!
    magnitudes *= magnitude_multipliers

    # normalize magnitudes
    norm_ratio = 1 / np.max(magnitudes)
    magnitudes *= norm_ratio

    # calculate values
    values = np.clip(np.floor(magnitudes * IMAGE_MAX_VALUE), 0, IMAGE_MAX_VALUE - 1)

    # calculate hues
    hues = (phases + PHASE_OFFSET) % TWO_PI
    hues = np.floor(hues * (IMAGE_MAX_VALUE / TWO_PI))

    # initialize image array
    hsv = np.zeros((frame_count, fft_size, 3), dtype=np.uint8)

    # fill image array
    hsv[:,:,0] = hues
    hsv[:,:,1] = IMAGE_SATURATION
    hsv[:,:,2] = values

    return hsv


def hsv2wave(
    hsv: np.ndarray,
    frame_size: int = 2048,
) -> np.ndarray:

    IMAGE_MAX_VALUE = 256
    PHASE_OFFSET = 0
    TWO_PI = 2 * np.pi

    fft_size = hsv.shape[1]

    # get hues and values
    hues = hsv[:,:,0]
    values = hsv[:,:,2]

    # calculate magnitudes
    # don't need to normalize now as we do it later
    magnitudes = values.astype(np.float64)

    # scale magnitudes by partial number
    magnitude_multipliers = np.arange(fft_size)
    magnitude_multipliers[0] = 1 # don't delete the DC offset!
    magnitudes *= (1 / magnitude_multipliers)

    # calculate phases
    phases = (hues * (TWO_PI / IMAGE_MAX_VALUE)) - PHASE_OFFSET

    # calculate complex form of partials
    frames_fft = magnitudes * np.exp(1j * phases)

    # inverse FFT frames in parallel
    frames: np.ndarray = scipy.fft.irfft(frames_fft, frame_size, axis=1)

    # flatten to wave
    wave = frames.flatten()

    # normalize wave
    norm_ratio = 1 / np.absolute(wave).max()
    wave *= norm_ratio

    return wave


# def main():
#     audio, rate = sf.read("data/sawdisp.wav")
#     img_array = wave2hsv(audio)
#     new_audio = hsv2wave(img_array).astype(np.float32)
#     sf.write("newsawdisp.wav", new_audio, samplerate=44100)

#     img = PIL.Image.fromarray(img_array, mode="HSV")
#     img = img.convert("RGB")
#     img = img.transpose(2) # rotate anti-clockwise 90 degrees
#     img.save("sawdisp.png")

# if __name__ == "__main__":
#     main()