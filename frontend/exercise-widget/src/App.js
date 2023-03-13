import React, { Component, useState } from "react";
import "./App.css";
import Annotatable from "./Annotatable";

// import "bootstrap/dist/css/bootstrap.min.css"
// import "bootstrap/dist/js/bootstrap.bundle.min"

function App () {
  const [contourVisible, setContour] = useState(false)
  const [resynthesisId, setResynthesisId] = useState(null)
  const [showResynthesisContour, setShowResynthesisContour] = useState(false)

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

  function playResynthesis() {
    if (resynthesisId !== null) {
      const audio = new Audio(`https://todi.cls.ru.nl/PraatResynthese/${resynthesisId}.mp3`)
      audio.play()
    }
  }

  function toggleContour() {
    setContour(b => !b)
  }

  function toggleResynthesisContour() {
    setShowResynthesisContour(b => !b)
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

  function resynthesize() {
    fetch("https://todi.cls.ru.nl/cgi-bin/synthese7b.pl", {
      "credentials": "omit",
      "headers": {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "frame",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
      },
      "referrer": "https://todi.cls.ru.nl/ToDI/ToDIpraat_7b/ex7b_1.htm",
      "body": `Generatie=Resynthesize&todi=109%3D%25L%2B${annotations[0]}%2B---%2B${annotations[1]}%2B---%2B${annotations[2]}%2B${annotations[3]}%2B---%2B${annotations[4]}%2B&var=No`,
      "method": "POST",
      "mode": "cors"
    }).then(r => r.text()).then(html => {
      console.log(html)
      const el = document.createElement('html')
      el.innerHTML = html
      const xpathSearch = document.evaluate('//meta[@http-equiv="refresh"]/@content', el, null, XPathResult.ANY_TYPE, null)
      const attribute = xpathSearch.iterateNext()
      const url = attribute.value.split('URL=')[1]
      return fetch(url)
    }).then(r => r.text())
      .then(html => {
        const match = html.match(/play_sound\('https:\/\/todi\.cls\.ru\.nl\/PraatResynthese\/(\d+)'\)/)
        if (match) {
          setResynthesisId(match[1])
        } else {
          // TODO: Error handling.
        }
      })
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
        <button onClick={toggleContour}>{contourVisible ? 'Hide' : 'Show'} contour</button>
        <button onClick={checkAnnotation}>Check</button>
        <button onClick={showSolution}>Key</button>
        <button onClick={resynthesize}>Resynthesize</button>
        <button disabled={resynthesisId === null} onClick={playResynthesis}>Play resynthesis</button>
        <button disabled={resynthesisId === null} onClick={toggleResynthesisContour}>{showResynthesisContour ? 'Hide' : 'Show'} resynthesis contour</button>
      </div>
      <img src="./img/109.png" alt="" style={{width: '100%', display: contourVisible ? 'block' : 'none'}}/>
      <img src={`https://todi.cls.ru.nl/PraatResynthese/${resynthesisId}.png`} alt=""
        style={{width: '100%', display: showResynthesisContour && resynthesisId !== null ? 'block' : 'none'}}/>
    </div>
  );
}

export default App;
