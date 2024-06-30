import matplotlib.pyplot as plt
import numpy as np
from chirp.inference.search.display import get_melspec_layer, plot_melspec
from etils import epath
from chirp import audio_utils
from scipy.io import wavfile

"""
Workflow:
Get examples (filename, species, timestamp_s)
Compute melspec and wav and save to disk with following structure:
filename^_^timestamp_s^_^species.png for melspec
filename^_^timestamp_s^_^species.wav for wav
"""

def precompute_example(
    filepath: epath.Path,
    species: str,
    timestamp_s: float,
    precompute_dir: epath.Path,
    sample_rate: int = 32000):
    """
    Precompute melspec and wav for a given example
    Args:
        filepath: epath.Path, path to the file
        species: str, species of the example
        timestamp_s: float, timestamp in seconds
        precompute_dir: epath.Path, path to the directory where to save the precomputed data
        sample_rate: int, sample rate of the audio file
    """
    
    filename = filepath.name
    melspec_path = precompute_dir / epath.Path(f"{filename}^_^{timestamp_s}^_^{species}.png")
    wav_path = precompute_dir / epath.Path(f"{filename}^_^{timestamp_s}^_^{species}.wav")
    
    if melspec_path.exists() and wav_path.exists():
        return
    
    # load audio
    start = int(timestamp_s * sample_rate)
    end = int((timestamp_s + 5) * sample_rate)
    audio = audio_utils.load_audio(filepath, sample_rate)[start:end]
    
    melspec_layer = get_melspec_layer(sample_rate)
    if audio.shape[0] < sample_rate / 100 + 1:
        # Center pad if audio is too short.
        zs = np.zeros([sample_rate // 10], dtype=audio.dtype)
        audio = np.concatenate([zs, audio, zs], axis=0)
    melspec = melspec_layer.apply({}, audio[np.newaxis, :])[0]
    plot_melspec(melspec, sample_rate=sample_rate, frame_rate=100)
    
    # save melspec
    plt.savefig(melspec_path)
    plt.close()
    
    # save wav
    with open(wav_path, "wb") as f:
        wavfile.write(f, sample_rate, np.float32(audio))