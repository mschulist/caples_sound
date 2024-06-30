import chirp.audio_utils as audio_utils
from etils import epath
import pandas as pd
from datetime import datetime


def get_next_precomputed_example(
    precompute_dir: epath.Path,
    labeled_path: epath.Path,
    sample_rate: int = 32000,
):
    """
    Get the next precomputed example
    Args:
        precompute_dir: epath.Path, path to the directory where the precomputed data is saved
        labeled_path: epath.Path, path to the directory where the labeled data is saved
        sample_rate: int, sample rate of the audio files
    Returns:
        audio: np.array, the audio data
        melspec_path: epath.Path, path to the melspec image
        filepaths: dict, dictionary with filepaths for possible annotations
    """

    # get the already labeled files
    # get the already labeled files
    finished_targets_path = labeled_path / epath.Path("finished_raven.csv")
    if not finished_targets_path.exists():
        with finished_targets_path.open("a") as f:
            f.write("start\n")
    already_labeled = set(
        pd.read_csv(labeled_path / epath.Path("finished_raven.csv"), header=None)
        .iloc[:, 0]
        .to_list()
    )

    # get the next audio file from the precompute directory
    precompute_files = [f.name for f in precompute_dir.glob("*.wav")]
    

    for f in precompute_files:
        if f in already_labeled:
            continue

        filename, timestamp_s, species = f.split("^_^")
        species = species.split(".")[0]  # get rid of the file extension

        audio = audio_utils.load_audio_file(precompute_dir / f, sample_rate)

        melspec_path = precompute_dir / epath.Path(
            f"{filename}^_^{timestamp_s}^_^{species}.png"
        )

        filepaths = {
            "song": labeled_path
            / epath.Path(f"{species}_song")
            / epath.Path(f"{filename}__{timestamp_s}.wav"),
            "call": labeled_path
            / epath.Path(f"{species}_call")
            / epath.Path(f"{filename}__{timestamp_s}.wav"),
        }

        # write to file to say that we have looked at this recording_path already
        with (labeled_path / epath.Path("finished_raven.csv")).open("a") as s:
            # just to keep track of when we looked at this recording_path
            s.write(f"{datetime.now()}\n")
            s.write(f"{f}\n") # no .wav at end

        return audio, melspec_path, filepaths

    return None, None, None
