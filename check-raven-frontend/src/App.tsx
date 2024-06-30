import { useState } from "react";
import "./App.css";

const SERVER_URL = "https://checkravenserver-efz2d6tgpa-uc.a.run.app";

function App() {
  const [melspec, setMelspec] = useState<string | ArrayBuffer | null>(null);
  const [audio, setAudio] = useState(null);
  const [filepaths, setFilepaths] = useState(null);
  const [annotated, setAnnotated] = useState(false);

  const getNextRecording = async () => {
    setAnnotated(false);
    setAudio(null);
    setMelspec(null);
    setFilepaths(null);
    const response = await fetch(`${SERVER_URL}/next-recording`);
    const { audio, melspec, filepaths } = await response.json();
    setAudio(audio);
    setMelspec(melspec);
    setFilepaths(filepaths);
  };


  console.log(filepaths);


  type FilePaths = {
    [key: string]: string;
  };

  const create_class_buttons = (fp: FilePaths) => {
    const type = Object.keys(fp)[0];
    const path = fp[type];
    const species_type = path.split("/").slice(-2)[0];
    const response_json = {
      'filepaths': fp,
      'type': type,
    }
    return (
      <button
        className="transition duration-300 ease-in-out bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-2 px-4 m-4 rounded"
        key={`${type}-${species_type}`}
        onClick={() => fetch(`${SERVER_URL}/annotate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(response_json),
        }).then(() => setAnnotated(true)
        )}
      >
        {species_type}
      </button>
    )
  }


  return (
    <div className="flex flex-col self-center items-center w-vw">
      <div className="flex flex-col self-center items-center w-1/2">
        <button
          className="transition duration-300 ease-in-out bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-2 px-4 rounded"
          onClick={getNextRecording}
        >
          Get Next Recording
        </button>
        {melspec && <img src={`data:image/png;base64, ${melspec}`} alt="melspec" className="m-6 rounded-md" />}
        {filepaths && <div> 
          {filepaths && <div>
            {
              Object.keys(filepaths).map((key) => {
                return (
                  <div key={key} className="m-2">
                    <span className="text-blue-500 font-bold">{key}:</span>{" "}
                    <span className="text-green-500">{filepaths[key]}</span>
                    <br />
                  </div>
                );
              })
            }
            </div>}
          </div>
        }
        {audio && (
          <audio controls src={`data:audio/wav;base64, ${audio}`} className="m-4"></audio>
        )}
        {filepaths &&
          Object.keys(filepaths).map((key) => {
            return create_class_buttons({ [key]: filepaths[key] });
          })}
          {annotated && <p>Annotation successful!</p>}
      </div>
    </div>
  );
}

export default App;
