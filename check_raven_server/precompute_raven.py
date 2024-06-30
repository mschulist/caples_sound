from precompute_example import precompute_example
from etils import epath
from chirp import audio_utils
import numpy as np
from scipy.io import wavfile
import pandas as pd
import argparse
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

"""
Script to precompute mel spectrograms and wav files for all raven examples
"""


def process_raven_example(raven_example, ARU_data_glob, precompute_dir, sample_rate):
    """
    Process a single raven example.
    Args:
        raven_example: pd.Series, a single row from the raven dataframe
        ARU_data_glob: str, glob pattern for ARU data
        precompute_dir: epath.Path, path to the directory where to save the precomputed data
        sample_rate: int, sample rate of the audio files
    """
    species = raven_example["label"]
    timestamp_s = raven_example["timestamp_s"]
    filename = epath.Path(raven_example["filename"])

    glob_path = epath.Path(ARU_data_glob) / filename
    ARU_files = [f for f in epath.Path("").glob(str(glob_path))]
    if len(ARU_files) == 0:
        raise ValueError(f"No ARU files found with glob {ARU_data_glob}")
    if len(ARU_files) > 1:
        Warning(
            f"Multiple ARU files found with glob {ARU_data_glob}. Using the first one."
        )

    filepath = ARU_files[0]

    precompute_example(filepath, species, timestamp_s, precompute_dir, sample_rate)


def precompute_raven(
    raven_annotations: epath.Path,
    precompute_dir: epath.Path,
    ARU_data_glob: str,
    sample_rate: int = 32000,
    max_workers: int = None,
):
    """
    Precompute mel spectrograms and wav files for all raven examples
    Args:
        raven_annotations: epath.Path, path to the raven annotations
        precompute_dir: epath.Path, path to the directory where to save the precomputed data
        ARU_data_glob: str, glob pattern for ARU data
        sample_rate: int, sample rate of the audio files
        max_workers: int, maximum number of processes to use
    """
    raven = pd.read_csv(raven_annotations)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(
                process_raven_example,
                raven_example,
                ARU_data_glob,
                precompute_dir,
                sample_rate,
            )
            for _, raven_example in raven.iterrows()
        ]

        for future in tqdm(as_completed(futures), total=len(raven)):
            try:
                future.result()
            except Exception as exc:
                print(f"Generated an exception: {exc}")


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
    parser.add_argument(
        "--max_workers",
        type=int,
        default=None,
        help="Maximum number of processes to use",
    )
    args = parser.parse_args()

    precompute_raven(
        raven_annotations=args.raven_annotations,
        precompute_dir=args.precompute_dir,
        ARU_data_glob=args.ARU_data_glob,
        sample_rate=args.sample_rate,
        max_workers=args.max_workers,
    )
