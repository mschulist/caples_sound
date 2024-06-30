from precompute_example import precompute_example
from etils import epath
from chirp import audio_utils
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pandas as pd
import argparse
from tqdm import tqdm
import threading

"""
Script to precompute mel spectrograms and wav files for all raven examples
"""


def precompute_raven(
    raven_annotations: epath.Path,
    precompute_dir: epath.Path,
    ARU_data_glob: str,
    sample_rate: int = 32000,
):
    """
    Precompute mel spectrograms and wav files for all raven examples
    Args:
        raven_dir: epath.Path, path to the directory where the raven examples are stored
        precompute_dir: epath.Path, path to the directory where to save the precomputed data
        sample_rate: int, sample rate of the audio files
    """

    # get all raven examples
    raven = pd.read_csv(raven_annotations)
    
    for i, raven_example in tqdm(raven.iterrows(), total=len(raven)):
        # get species and timestamp from the filename
        species = raven_example["label"]
        timestamp_s = raven_example["timestamp_s"]
        filename = epath.Path(raven_example["filename"])

        # get all the file that corresponds with the ARU data glob
        # TODO: for cloud version, support gs://
        print(ARU_data_glob)
        print(filename)
        glob_path = epath.Path(ARU_data_glob) / filename
        ARU_files = [f for f in epath.Path("").glob(str(glob_path))]
        if len(ARU_files) == 0:
            raise ValueError(f"No ARU files found with glob {ARU_data_glob}")
        if len(ARU_files) > 1:
            Warning(
                f"Multiple ARU files found with glob {ARU_data_glob}. Using the first one."
            )

        filepath = ARU_files[0]

        # precompute melspec and wav
        precompute_example(filepath, species, timestamp_s, precompute_dir, sample_rate)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Precompute mel spectrograms and wav files for all raven examples"
    )
    parser.add_argument(
        "-ra",
        "--raven_annotations",
        type=epath.Path,
        help="Path to the raven annotations",
    )
    parser.add_argument(
        "-pd",
        "--precompute_dir",
        type=epath.Path,
        help="Path to the directory where to save the precomputed data",
    )
    parser.add_argument(
        "-adg",
        "--ARU_data_glob",
        type=str,
        help='Glob for the ARU data: e.g. "ARU_data_all/*/"',
    )
    parser.add_argument(
        "--sample_rate", type=int, default=32000, help="Sample rate of the audio files"
    )
    args = parser.parse_args()
    print(args)

    precompute_raven(
        raven_annotations=args.raven_annotations, 
        precompute_dir=args.precompute_dir, 
        ARU_data_glob=args.ARU_data_glob,
        sample_rate=args.sample_rate)
