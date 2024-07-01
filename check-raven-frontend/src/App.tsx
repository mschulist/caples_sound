import { useState } from "react";
import { hash, compare } from 'bcryptjs';
import "./App.css";
import Directions from "./components/Directions";

const SERVER_URL = "https://checkravenserver-efz2d6tgpa-uc.a.run.app";

const PASSHASH = "$2b$10$8/PNvJwWiD4BNeldHwPYyu4CR1axfPR9wQTtd/YgWt/005TGsTezy";

function App() {
  const [melspec, setMelspec] = useState<string | ArrayBuffer | null>(null);
  const [audio, setAudio] = useState(null);
  const [filepaths, setFilepaths] = useState(null);
  const [annotated, setAnnotated] = useState(false);
  const [password, setPassword] = useState("");
  const [authenticated, setAuthenticated] = useState(false);

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


  type FilePaths = {
    [key: string]: string;
  };

  const finishAnnotation = () => {
    setAnnotated(true);
    getNextRecording();
  };

  const create_class_buttons = (fp: FilePaths) => {
    const type = Object.keys(fp)[0];
    const path = fp[type];
    const species_type = path.split("/").slice(-2)[0];
    const response_json = {
      filepaths: fp,
      type: type,
    };
    return (
      <button
        className="transition duration-300 ease-in-out bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-2 px-4 m-4 rounded self-center"
        key={`${type}-${species_type}`}
        onClick={() =>
          fetch(`${SERVER_URL}/annotate`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(response_json),
          }).then(() => finishAnnotation())
        }
      >
        {species_type}
      </button>
    );
  };

  return (
    <div className="w-screen h-screen">
      {!authenticated && (
        <div className="flex flex-col self-center h-full px-16 justify-center">
          <input
            type="password"
            className="rounded-md p-2 m-4 text-black self-center"
            placeholder="Enter password"
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            className="transition duration-300 ease-in-out bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-2 px-4 rounded self-center"
            onClick={() => {
              compare(password, PASSHASH, (_: any, res: boolean) => {
                if (res) {
                  setAuthenticated(true);
                } else {
                  alert("Incorrect password");
                }
              });
            }}
          >
            Authenticate
          </button>
        </div>
      )}
      {authenticated && (
        <div className="flex self-center py-10 h-full px-16">
          <div className="flex flex-col w-1/4 justify-center">
            <Directions />
          </div>
          <div className="flex flex-col w-1/2">
            <button
              className="transition duration-300 ease-in-out bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-700 hover:to-gray-800 text-white font-bold py-2 px-4 rounded self-center"
              onClick={getNextRecording}
            >
              Get Next Recording
            </button>
            {melspec && (
              <img
                src={`data:image/png;base64, ${melspec}`}
                alt="melspec"
                className="m-6 rounded-md"
              />
            )}
            {audio && (
              <audio
                controls
                src={`data:audio/wav;base64, ${audio}`}
                className="m-4 self-center"
              ></audio>
            )}
            {filepaths &&
              Object.keys(filepaths).map((key) => {
                return create_class_buttons({ [key]: filepaths[key] });
              })}
            {annotated && <p>Annotation successful!</p>}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
