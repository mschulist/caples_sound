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
    species: str,
    precompute_dir: epath.Path,
    filepath: epath.Path,
    timestamp_s: float,
    audio: np.ndarray | None = None,
    sample_rate: int = 32000,
):
    """
    Precomputes and saves a mel spectrogram and a WAV file for a given audio segment.

    Args:
        species (str): The species of the audio.
        precompute_dir (epath.Path): The directory to save the precomputed files.
        filepath (epath.Path ): The path to the audio file.
        timestamp_s (float): The starting timestamp of the audio segment.
        audio (np.ndarray | None, optional): The audio data. Defaults to None.
        sample_rate (int, optional): The sample rate of the audio. Defaults to 32000.

        If you provide an audio, you still must provide a filepath and timestamp_s,
        but the audio will be used instead of loading the audio from the filepath.
    """

    filename = filepath.name
    melspec_path = precompute_dir / epath.Path(
        f"{filename}^_^{timestamp_s}^_^{species}.png"
    )
    wav_path = precompute_dir / epath.Path(
        f"{filename}^_^{timestamp_s}^_^{species}.wav"
    )

    if melspec_path.exists() and wav_path.exists():
        return

    # load audio
    if audio is None:
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
