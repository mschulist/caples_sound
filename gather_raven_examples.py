import collections
from etils import epath
from ml_collections import config_dict
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tqdm import tqdm
import pandas as pd
from typing import List

from chirp import audio_utils
from chirp.inference import interface
from chirp.inference import tf_examples
from chirp.inference import models
from chirp.models import metrics
from chirp.taxonomy import namespace
from chirp.inference.search import bootstrap
from chirp.inference.search import search
from chirp.inference.search import display
from chirp.inference.classify import classify
from chirp.inference.classify import data_lib
from scipy.io import wavfile
import os


def search_single_recording(
    recording_path: epath.Path|str, 
    labeled_path: epath.Path|str,
    species_code: str, 
    types: List[str],
    target_score: float|None, 
    sample_rate, 
    project_state, 
    bootstrap_config,
    timestamp_s: float = 0.0,
    ):
    
    audio = audio_utils.load_audio_file(recording_path, sample_rate)
    start = int(timestamp_s * sample_rate)
    end = int(5 * sample_rate) + int(timestamp_s * sample_rate)
    audio = audio[start:end]
    outputs = project_state.embedding_model.embed(audio)
    query = outputs.pooled_embeddings('first', 'first')
    print(f'Recording: {recording_path}, species: {species_code}, timestamp: {timestamp_s}')
    display.plot_audio_melspec(audio, sample_rate)
    
    
    top_k = 10
    metric = 'mip'
    random_sample = False
    ds = project_state.create_embeddings_dataset(shuffle_files=True)
    results, all_scores = search.search_embeddings_parallel(
        ds, query,
        hop_size_s=bootstrap_config.embedding_hop_size_s,
        top_k=top_k, target_score=target_score, score_fn=metric,
        random_sample=random_sample)

    samples_per_page = 10
    page_state = display.PageState(
        np.ceil(len(results.search_results) / samples_per_page))

    # get labels
    labels = ['unknown']
    for type in types:
        labels.append(f'{species_code}_{type}')

    display.display_paged_results(
        results, page_state, samples_per_page,
        project_state=project_state,
        embedding_sample_rate=project_state.embedding_model.sample_rate,
        exclusive_labels=False,
        checkbox_labels=labels,
        max_workers=5,
    )

    # write to file to say that we have looked at this recording_path already
    with (labeled_path / epath.Path('finished_raven.csv')).open('a') as f:
        f.write(f'{recording_path}\n')
    
    return results


def search_raven(
    raven_annotations: pd.DataFrame,
    ARU_path: epath.Path,
    labeled_path: epath.Path,
    project_state,
    bootstrap_config,
    target_score: float|None = None,
    sample_rate: int = 32000,
):
    # get the filepath (complete) from the raven table
    r = raven_annotations.copy()
    year = r['filename'].str.split('_').str[1].str[0:4]
    r['filepath'] = str(ARU_path) + '/' + year + '/' + r['filename']
    
    # get the already labeled files
    finished_targets_path = labeled_path / epath.Path('finished_raven.csv')
    if not finished_targets_path.exists():
        with finished_targets_path.open('a') as f:
            f.write('start\n')
    already_labeled = set(pd.read_csv(
        labeled_path / epath.Path('finished_raven.csv'), 
        header=None).iloc[:,0].to_list())
    
    for i, row in r.iterrows():
        if row['filepath'] in already_labeled:
            continue
        print(row['filepath'])
        results = search_single_recording(recording_path=row['filepath'],
                                    labeled_path=labeled_path,
                                    species_code=row['label'],
                                    types=['song', 'call'],
                                    target_score=target_score,
                                    sample_rate=sample_rate,
                                    project_state=project_state, 
                                    bootstrap_config=bootstrap_config,
                                    timestamp_s=row['timestamp_s'])
        return results
        

def display_raven_recording(
    raven_annotations: pd.DataFrame,
    ARU_path: epath.Path,
    labeled_path: epath.Path
    ) -> list[np.ndarray, dict[str, epath.Path]]:
    
    # get the next audio file from the raven table
    r = raven_annotations.copy()
    year = r['filename'].str.split('_').str[1].str[0:4]
    r['filepath'] = str(ARU_path) + '/' + year + '/' + r['filename']
    
    # get the already labeled files
    finished_targets_path = labeled_path / epath.Path('finished_raven.csv')
    if not finished_targets_path.exists():
        with finished_targets_path.open('a') as f:
            f.write('start\n')
    already_labeled = set(pd.read_csv(
        labeled_path / epath.Path('finished_raven.csv'), 
        header=None).iloc[:,0].to_list())
    
    for i, row in r.iterrows():
        current_already_labeled = f"{row['filepath']}^_^{row['timestamp_s']}^_^{row['label']}"
        if current_already_labeled in already_labeled:
            continue
        print(row['filepath'])
        filename = f"{row['filename'].split('.')[0]}__{row['timestamp_s']}.wav"
        filepaths = {
            'song': labeled_path / epath.Path(f"{row['label']}_song") / epath.Path(filename),
            'call': labeled_path / epath.Path(f"{row['label']}_call") / epath.Path(filename),
        }
        audio = audio_utils.load_audio_file(row['filepath'], 32000)
        start = int(row['timestamp_s'] * 32000)
        end = int(5 * 32000) + int(row['timestamp_s'] * 32000)
        audio = audio[start:end]
        print(f'Recording: {row["filepath"]}, species: {row["label"]}, timestamp: {row["timestamp_s"]}')
        display.plot_audio_melspec(audio, 32000)
        
        # write to file to say that we have looked at this recording_path already
        with (labeled_path / epath.Path('finished_raven.csv')).open('a') as f:
            f.write(f'{current_already_labeled}\n')
        
        
        return audio, filepaths
    
    
def write_raven_annotations(
    audio: np.ndarray, 
    filepaths: dict[str, epath.Path], 
    type: str,
    sample_rate: float = 32000) -> None:
    
    if type not in filepaths:
        raise ValueError(f'No filepaths for type {type}')
    
    f = filepaths[type]
    
    with f.open('wb') as f:
        wavfile.write(f, sample_rate, np.float32(audio))