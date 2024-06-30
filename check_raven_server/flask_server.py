import base64
from flask import Flask, request
from get_melspec import plot_audio_melspec
from gather_raven_examples import display_raven_recording, write_raven_annotations
import numpy as np
import pandas as pd
from etils import epath
import io
from scipy.io.wavfile import write
from flask_cors import CORS
import chirp.audio_utils as audio_utils
import librosa

# Load Raven annotations
raven = pd.read_csv("../comparison/raven_annotations_even.csv")

sample_rate = 32000

ARU_data_path = '../ARU_data_all'

app = Flask(__name__)
CORS(app)

@app.route("/next-recording", methods=["GET"])
def next_recording():
    # Get the audio for the next recording
    audio, fp = display_raven_recording(
        raven_annotations=raven,
        ARU_path=epath.Path(ARU_data_path),
        labeled_path=epath.Path("../labeled_outputs"),
    )
    

    # Plot the melspec and save it to a file
    melspec_path = plot_audio_melspec(audio, sample_rate)
    
    audio = librosa.util.normalize(audio)

    # Get the image in base64
    with open(melspec_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Get the audio in base64
    audio_base64 = io.BytesIO()
    write(audio_base64, sample_rate, audio)
    audio_base64.seek(0)
    wav_bytes = audio_base64.read()

    audio_data = base64.b64encode(wav_bytes).decode("utf-8")

    # Convert the filepaths to strings
    fps = {k: str(v) for k, v in fp.items()}

    # Send back [audio data, melspec_path, filepaths for possible annotations]
    return {"audio": audio_data, "melspec": image_data, "filepaths": fps}

@app.route("/annotate", methods=["POST"])
def annotate():
    # Get the annotation data
    data = request.json
    
    print(data['filepaths'])


    filepaths = data["filepaths"]
    annotation_type = data["type"]
    
    fp = filepaths[annotation_type]
    
    audio_path, timestamp_s = fp.split("/")[-1].split("__")[0:2]
    timestamp_s = float(timestamp_s.split(".")[0])
    year = audio_path.split("_")[1][0:4]
    audio_path = epath.Path(f'{ARU_data_path}/{year}/{audio_path}.wav')
    audio = audio_utils.load_audio(audio_path, sample_rate)
    audio = audio[int(timestamp_s * sample_rate) : int(timestamp_s * sample_rate) + 5 * sample_rate]
    
    # convert fp to Path object
    filepaths = {k: epath.Path(v) for k, v in filepaths.items()}
    

    # Write the annotation to the file
    write_raven_annotations(audio=audio, filepaths=filepaths, type=annotation_type)

    return {"status": "success"}

if __name__ == "__main__":
    app.run(debug=True)
