import base64
from flask import Flask, request
from gather_precomputed_examples import get_next_precomputed_example
import numpy as np
import pandas as pd
from etils import epath
import io
from scipy.io.wavfile import write
from flask_cors import CORS
import chirp.audio_utils as audio_utils
from scipy.io import wavfile
import librosa

import google.cloud.storage as gcs

sample_rate = 32000

precompute_dir = epath.Path("gs://bird-ml/caples-data/precomputed_raven")
labeled_path = epath.Path("gs://bird-ml/caples-data/labeled_outputs")

app = Flask(__name__)
CORS(app)


@app.route("/next-recording", methods=["GET"])
def next_recording():
    # Get the audio for the next recording
    audio, melspec_path, fps = get_next_precomputed_example(
        precompute_dir=precompute_dir,
        labeled_path=labeled_path,
    )

    if audio is None:
        return {"status": "NO MORE RECORDINGS"}

    audio = librosa.util.normalize(audio)  # just for listening, not for processing...

    # Get the image in base64
    with melspec_path.open("rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Get the audio in base64
    audio_base64 = io.BytesIO()
    write(audio_base64, sample_rate, audio)
    audio_base64.seek(0)
    wav_bytes = audio_base64.read()

    audio_data = base64.b64encode(wav_bytes).decode("utf-8")

    # Convert the filepaths to strings
    fps = {k: str(v) for k, v in fps.items()}

    # Send back [audio data, melspec_path, filepaths for possible annotations]
    return {"audio": audio_data, "melspec": image_data, "filepaths": fps}


@app.route("/annotate", methods=["POST"])
def annotate():
    # Get the annotation data
    data = request.json

    print(data["filepaths"])

    filepaths: str = data["filepaths"]
    annotation_type: str = data["type"]

    fp: str = filepaths[annotation_type]

    audio_path, timestamp_s = fp.split("/")[-1].split("__")[0:2]
    timestamp_s = float(timestamp_s.split(".")[0])

    audio_path = list(precompute_dir.glob(f"{str(audio_path)}^_^{timestamp_s}*.wav"))[0]

    # convert fp to Path object
    filepaths = {
        k: epath.Path(v.replace(".wav", "", 1)) for k, v in filepaths.items()
    }

    # Write the annotation to the file
    if annotation_type not in filepaths:
        raise ValueError(f"No filepaths for type {type}")
    
    audio_path.copy(filepaths[annotation_type])

    return {"status": "Annotation saved"}


if __name__ == "__main__":
    app.run(debug=True)
