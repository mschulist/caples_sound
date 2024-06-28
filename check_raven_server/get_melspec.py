import matplotlib.pyplot as plt
import numpy as np
import librosa
from librosa import display as librosa_display
from chirp.models import frontend
import os
from chirp.inference.search.display import get_melspec_layer, plot_melspec
import tempfile


def plot_audio_melspec(
    audio: np.ndarray,
    sample_rate: int,
) -> str:
    """Plot a melspectrogram from audio and return the filename of the saved image."""
    melspec_layer = get_melspec_layer(sample_rate)
    if audio.shape[0] < sample_rate / 100 + 1:
        # Center pad if audio is too short.
        zs = np.zeros([sample_rate // 10], dtype=audio.dtype)
        audio = np.concatenate([zs, audio, zs], axis=0)
    melspec = melspec_layer.apply({}, audio[np.newaxis, :])[0]
    plot_melspec(melspec, sample_rate=sample_rate, frame_rate=100)
    # save fig to temp file
    temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(temp.name)
    return temp.name