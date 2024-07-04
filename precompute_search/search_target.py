from etils import epath
from typing import List
from chirp import audio_utils
from chirp.inference.search import search
from chirp.inference.search import bootstrap
from precompute_example import precompute_example


def search_single_recording(
    recording_path: epath.Path,
    target_score: float | None,
    sample_rate: int,
    project_state: bootstrap.BootstrapState,
    bootstrap_config: bootstrap.BootstrapConfig,
) -> search.TopKSearchResults:
    """
    Searches for a single recording in the embeddings dataset.

    Args:
        recording_path (epath.Path): The path to the recording file.
        target_score (float | None): The target score to filter the search results. If None, all results are returned.
        sample_rate (int): The sample rate of the recording.
        project_state (BootstrapState): The state of the project.
        bootstrap_config (BootstrapConfig): The configuration for bootstrapping.

    Returns:
        results (TopKSearchResults): The search results.
    """

    audio = audio_utils.load_audio_file(recording_path, sample_rate)
    outputs = project_state.embedding_model.embed(audio)
    query = outputs.pooled_embeddings("first", "first")

    ds = project_state.create_embeddings_dataset(shuffle_files=True)
    results, _ = search.search_embeddings_parallel(
        embeddings_dataset=ds,
        query_embedding_batch=query,
        hop_size_s=bootstrap_config.embedding_hop_size_s,
        top_k=10,
        target_score=target_score,
        score_fn="mip",
    )

    return results


def precompute_search(
    search_results: search.TopKSearchResults,
    project_state: bootstrap.BootstrapState,
    species_code: str,
    precompute_dir: epath.Path,
    sample_rate: int = 32000,
) -> None:
    """
    Precomputes the spectrograms and audio files for the search results.

    Args:
        search_results (List[SearchResult]): The search results.
        project_state (BootstrapState): The BootstrapState from the embeddings.
        species_code (str): The species code.
        precompute_dir (epath.Path): The directory to save the precomputed files.
        sample_rate (int): The sample rate of the model. Defaults to 32000.
    """

    results_iterator = project_state.search_results_audio_iterator(
        search_results=search_results,
    )

    for result in results_iterator:
        audio = result.audio
        if audio is None:
            continue
        filepath = epath.Path(result.filename)
        timestamp_s = float(result.timestamp_offset)

        precompute_example(
            species=species_code,
            precompute_dir=precompute_dir,
            filepath=filepath,
            timestamp_s=timestamp_s,
            audio=audio,
            sample_rate=sample_rate,
        )

def precompute_search_single_target(
    recording_path: epath.Path,
    target_score: float | None,
    sample_rate: int,
    project_state: bootstrap.BootstrapState,
    bootstrap_config: bootstrap.BootstrapConfig,
    species_code: str,
    precompute_dir: epath.Path,
) -> None:
    """
    Precomputes the search results for a single target recording.

    Args:
        recording_path (epath.Path): The path to the target recording file. Must be 5 seconds long. 
        target_score (float | None): The target score to filter the search results. If None, all results are returned.
        sample_rate (int): The sample rate of the model. 
        project_state (BootstrapState): The state of the project.
        bootstrap_config (BootstrapConfig): The configuration for bootstrapping.
        species_code (str): The species code.
        precompute_dir (epath.Path): The directory to save the precomputed files.
    """

    search_results = search_single_recording(
        recording_path=recording_path,
        target_score=target_score,
        sample_rate=sample_rate,
        project_state=project_state,
        bootstrap_config=bootstrap_config,
    )

    precompute_search(
        search_results=search_results,
        project_state=project_state,
        species_code=species_code,
        precompute_dir=precompute_dir,
        sample_rate=sample_rate,
    )