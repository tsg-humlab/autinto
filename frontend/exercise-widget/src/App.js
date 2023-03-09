import React, { Component, useState } from "react";
import "./App.css";
import Annotatable from "./Annotatable";

// import "bootstrap/dist/css/bootstrap.min.css"
// import "bootstrap/dist/js/bootstrap.bundle.min"

function App () {
  const [contourVisible, setContour] = useState(false)

  const startOptions = [
    ["%L", "!%L"],
    ["%H", "!%H"],
    ["%HL", "!%HL"],
  ];
  const wordOptions = [
    ["H*", "!H*"],
    ["H*L", "!H*L"],
    ["L*", "L*H"],
    ["L*HL", "L*!HL"],
    ["H*LH", "∅"],
  ];
  const endOptions = [["L%"], ["H%"], ["%"]];


  function playAudio() {
    const audio = new Audio('audio/109.mp3')
    audio.play()
  }

  function toggleContour() {
    setContour(b => !b)
  }

  return (
    <div className="App">
      <div className="text">
        <Annotatable preset="%L" />
        <Annotatable options={wordOptions} text="Dat" /> weet ik{" "}
        <Annotatable options={wordOptions} text="ook" /> niet
        <Annotatable options={endOptions} />
        <Annotatable options={[["H", "L"], ["∅", ""]]} text="zei de" />
        <span style={{whiteSpace: 'nowrap'}}>
          traploper
        <Annotatable options={endOptions} />
        </span>
      </div>
      <div className="button-container ml-3">
        <button className="btn btn-primary mt-3 pl-1" onClick={playAudio}>Play</button>
        <button onClick={toggleContour}>{contourVisible ? 'Hide contour' : 'Show contour'}</button>
      </div>
      <img src="./img/109.png" alt="" style={{width: '100%', display: contourVisible ? 'block' : 'none'}}/>
    </div>
  );
}

export default App;
