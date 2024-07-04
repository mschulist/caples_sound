from search_target import precompute_search_single_target
from etils import epath
from chirp.inference.search import bootstrap
import argparse
import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

"""
Script to precompute mel spectrograms and wav files for all target recordings
"""


def process_target_recording(
    target_recording_path: epath.Path,
    project_state: bootstrap.BootstrapState,
    bootstrap_config: bootstrap.BootstrapConfig,
    precompute_dir: epath.Path,
):
    """
    Process a single target recording.
    Args:
        target_recording_path: epath.Path, path to the target recording
        project_state: bootstrap.BootstrapState, project state
        bootstrap_config: bootstrap.BootstrapConfig, project config
        precompute_dir: epath.Path, path to the directory where to save the precomputed data
    """
    species = target_recording_path.parent.name.split("_")[0]
    precompute_search_single_target(
        recording_path=target_recording_path,
        target_score=None,
        sample_rate=bootstrap_config.model_config["sample_rate"],
        project_state=project_state,
        bootstrap_config=bootstrap_config,
        species_code=species,
        precompute_dir=precompute_dir,
    )


def main(
    embeddings_path: epath.Path,
    precompute_dir: epath.Path,
    target_recordings_path: epath.Path,
    labeled_outputs_path: epath.Path,
):
    """
    Precomputes search targets for a given set of target recordings.

    Args:
        embeddings_path (epath.Path): The path to the embeddings file.
        precompute_dir (epath.Path): The directory to store the precomputed search targets.
        target_recordings_path (epath.Path): The path to the target recordings.
        labeled_outputs_path (epath.Path): The path to the labeled outputs.
    """

    if not precompute_dir.exists():
        precompute_dir.mkdir(parents=True)
    if not labeled_outputs_path.exists():
        labeled_outputs_path.mkdir(parents=True)

    bootstrap_config = bootstrap.BootstrapConfig.load_from_embedding_path(
        embeddings_path=embeddings_path, annotated_path=labeled_outputs_path
    )
    project_state = bootstrap.BootstrapState(config=bootstrap_config)

    target_recordings_globs = list(target_recordings_path.glob("*/*.wav"))

    for target_recording_path in tqdm.tqdm(
        target_recordings_globs, total=len(target_recordings_globs)
    ):
        process_target_recording(
            target_recording_path=target_recording_path,
            project_state=project_state,
            bootstrap_config=bootstrap_config,
            precompute_dir=precompute_dir,
        )


if __name__ == "__main__":
    """
    Example usage:
    python precompute_search_targets_script.py \
        -ep /path/to/embeddings/ \
        -pd /path/to/precompute_dir/ \
        -trp /path/to/target_recordings/ \
        -lop /path/to/labeled_outputs/ 
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-ep", "--embeddings_path", type=epath.Path, required=True)
    parser.add_argument("-pd", "--precompute_dir", type=epath.Path, required=True)
    parser.add_argument(
        "-trp", "--target_recordings_path", type=epath.Path, required=True
    )
    parser.add_argument(
        "-lop", "--labeled_outputs_path", type=epath.Path, required=True
    )
    args = parser.parse_args()

    main(
        embeddings_path=args.embeddings_path,
        precompute_dir=args.precompute_dir,
        target_recordings_path=args.target_recordings_path,
        labeled_outputs_path=args.labeled_outputs_path,
    )
