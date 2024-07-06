python gather_target_recordings/gather_target_recordings.py \
    --species_codes naswar \
    --n 5 \
    --target_path gs://bird-ml/caples-data/target_recordings_test \
    --runner DataflowRunner \
    --project ${1} \
    --region us-central1 \
    --num_workers 5 \
    --max_num_workers 5 \
    --requirements_file precompute_search/beam_docker_image/requirements.txt