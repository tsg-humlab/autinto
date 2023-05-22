import React, { Component, useState, useEffect, useRef, useCallback } from "react"
import * as R from "ramda"
import "./App.css"
import Annotatable from "./Annotatable"
import { readSpecification } from './specification.js'

import { register } from 'swiper/element/bundle'

register()

function fetchExercise(path) {
  return fetch(path).then(res => res.json())
}


function App({ id='' }) {
  const [contourVisible, setContour] = useState(false)
  const [resynthesisId, setResynthesisId] = useState(null)
  const [showResynthesisContour, setShowResynthesisContour] = useState(false)
  const [exerciseData, setExerciseData] = useState(null)
  const [annotations, setAnnotations] = useState(null)
  const [selectedItem, setSelectedItem] = useState(0)

  const swiperRef = useCallback(ref => {
    ref.swiper.on('activeIndexChange', (e) => setSelectedItem(e.activeIndex))
  }, [])


  useEffect(() => {
    fetchExercise(id).then((data) => {
      // TODO: Validate data!
      const spec = readSpecification(data)
      setExerciseData(spec)
      setAnnotations(spec.map(item => item.key.map(() => '')))
    })
  }, [])

  function playAudio() {
    const item = selectedItem
    if (item !== null) {
      const audio = new Audio(`audio/${exerciseData[item].audio}`)
      audio.play()
    }
  }

  function playResynthesis() {
    if (resynthesisId !== null) {
      const audio = new Audio(
        `https://todi.cls.ru.nl/PraatResynthese/${resynthesisId}.mp3`
      )
      audio.play()
    }
  }

  function toggleContour() {
    setContour((b) => !b)
  }

  function toggleResynthesisContour() {
    setShowResynthesisContour((b) => !b)
  }


  const updateAnnotation = (itemIndex, at) => (val) => {
    setAnnotations(a => R.adjust(itemIndex, R.update(at, val), a))
  }

  function checkAnnotation() {
    // TODO: Nicer equality comparison
    alert(
      `Answer is ${
        JSON.stringify(annotations[selectedItem]) === JSON.stringify(exerciseData && exerciseData[selectedItem].key)
          ? "correct"
          : "not correct"
      }`
    )
  }

  function showSolution() {
    if (exerciseData !== null) {
      setAnnotations(R.update(selectedItem, exerciseData[selectedItem].key, annotations))
    }
  }

  function resynthesize() {
    fetch("https://todi.cls.ru.nl/cgi-bin/synthese7b.pl", {
      credentials: "omit",
      headers: {
        "User-Agent":
          "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
        Accept:
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "frame",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Sec-GPC": "1",
        Pragma: "no-cache",
        "Cache-Control": "no-cache",
      },
      referrer: "https://todi.cls.ru.nl/ToDI/ToDIpraat_7b/ex7b_1.htm",
      body: `Generatie=Resynthesize&todi=109%3D%25L%2B${annotations[0]}%2B---%2B${annotations[1]}%2B---%2B${annotations[2]}%2B${annotations[3]}%2B---%2B${annotations[4]}%2B&var=No`,
      method: "POST",
      mode: "cors",
    })
      .then((r) => r.text())
      .then((html) => {
        const el = document.createElement("html")
        el.innerHTML = html
        const xpathSearch = document.evaluate(
          '//meta[@http-equiv="refresh"]/@content',
          el,
          null,
          XPathResult.ANY_TYPE,
          null
        )
        const attribute = xpathSearch.iterateNext()
        const url = attribute.value.split("URL=")[1]
        return fetch(url)
      })
      .then((r) => r.text())
      .then((html) => {
        const match = html.match(
          /play_sound\('https:\/\/todi\.cls\.ru\.nl\/PraatResynthese\/(\d+)'\)/
        )
        if (match) {
          setResynthesisId(match[1])
        } else {
          // TODO: Error handling.
        }
      })
  }

  return (
    <div className="App">
      <swiper-container ref={swiperRef} navigation="true" className="exercise-slider">
        {exerciseData !== null &&
            exerciseData.map((item, itemIndex) => 
            <swiper-slide>
              <div className="text">
                {item !== null &&
                    item.blocks.map((annotatable, key) =>
                      // JSON.stringify(annotatable)
                      R.is(String, annotatable) ? (
                        <> {annotatable} </>
                      ) : annotatable.index === null ? (
                        <Annotatable key={key} annotation={annotatable.choices} />
                      ) : (
                        <Annotatable
                          key={key}
                          annotation={annotations[itemIndex][annotatable.index]}
                          options={annotatable.choices}
                          onSelect={updateAnnotation(itemIndex, annotatable.index)}
                          text={annotatable.text}
                        />
                      )
                    )}
              </div>
            </swiper-slide>
        )}
      </swiper-container>
      <div className="button-container ml-3">
        <button className="btn btn-primary mt-3 pl-1" onClick={playAudio}>
          Play
        </button>
        <button onClick={toggleContour}>
          {contourVisible ? "Hide" : "Show"} contour
        </button>
        <button onClick={checkAnnotation}>Check</button>
        <button onClick={showSolution}>Key</button>
        <button onClick={resynthesize}>Resynthesize</button>
        <button disabled={resynthesisId === null} onClick={playResynthesis}>
          Play resynthesis
        </button>
        <button
          disabled={resynthesisId === null}
          onClick={toggleResynthesisContour}
        >
          {showResynthesisContour ? "Hide" : "Show"} resynthesis contour
        </button>
      </div>
      <img
        src={exerciseData !== null && selectedItem !== null ? `./img/${exerciseData[selectedItem].contour}` : undefined}
        alt=""
        style={{ width: "100%", display: contourVisible ? "block" : "none" }}
      />
      
      <img
        src={resynthesisId !== null ? `https://todi.cls.ru.nl/PraatResynthese/${resynthesisId}.png` : undefined}
        alt=""
        style={{
          width: "100%",
          display:
            showResynthesisContour && resynthesisId !== null ? "block" : "none",
        }}
      />
    </div>
  )
}

export default App
