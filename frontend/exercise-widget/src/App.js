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

  const solution = ["H*L", "H*L", "L%", "L", "L%"]

  function playAudio() {
    const audio = new Audio('audio/109.mp3')
    audio.play()
  }

  function toggleContour() {
    setContour(b => !b)
  }

  const [annotations, setAnnotation] = useState(['', '', '', '', ''])

  const updateAnnotation = at => val => {
    setAnnotation(a => a.map((e, i) => i === at ? val : e))
  }

  function checkAnnotation() {
    // TODO: Nicer equality comparison
    alert(`Answer is ${JSON.stringify(annotations) === JSON.stringify(solution) ? 'correct' : 'not correct'}`)
  }

  function showSolution() {
    setAnnotation(solution)
  }


  return (
    <div className="App">
      <div className="text">
        <Annotatable annotation="%L" />
        <Annotatable annotation={annotations[0]} options={wordOptions} text="Dat" onSelect={updateAnnotation(0)}/> weet ik{" "}
        <Annotatable annotation={annotations[1]} options={wordOptions} text="ook" onSelect={updateAnnotation(1)} /> niet
        <Annotatable annotation={annotations[2]} options={endOptions} onSelect={updateAnnotation(2)} />
        <Annotatable annotation={annotations[3]} options={[["H", "L"], ["∅", ""]]} text="zei de" onSelect={updateAnnotation(3)} />
        <span style={{whiteSpace: 'nowrap'}}>
          traploper
        <Annotatable annotation={annotations[4]} options={endOptions} onSelect={updateAnnotation(4)} />
        </span>
      </div>
      <div className="button-container ml-3">
        <button className="btn btn-primary mt-3 pl-1" onClick={playAudio}>Play</button>
        <button onClick={toggleContour}>{contourVisible ? 'Hide contour' : 'Show contour'}</button>
        <button onClick={checkAnnotation}>Check</button>
        <button onClick={showSolution}>Key</button>
      </div>
      <img src="./img/109.png" alt="" style={{width: '100%', display: contourVisible ? 'block' : 'none'}}/>
    </div>
  );
}

export default App;
