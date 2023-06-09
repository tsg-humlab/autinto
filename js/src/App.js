import React, {
  Component,
  useState,
  useEffect,
  useRef,
  useCallback,
} from 'react'
import * as R from 'ramda'
import './App.css'
import Annotatable from './Annotatable'
import Parameters from "./Parameters"
import { readSpecification } from './specification.js'
import { illegalInputHandling } from './validate.js'

import { register } from 'swiper/element/bundle'

register()

function fetchExercise(path) {
  return fetch(path).then((res) => res.json())
}

function App({ id = '' }) {
  const [contourVisible, setContour] = useState(false)
  const [resynthesisData, setResynthesisData] = useState(null)
  const [showResynthesisContour, setShowResynthesisContour] = useState(false)
  const [exerciseData, setExerciseData] = useState(null)
  const [annotations, setAnnotations] = useState(null)
  const [selectedItem, setSelectedItem] = useState(0)
  const [customSettingsEnabled, setCustomSettingsEnabled] = useState(false)
  const [parameterSettings, setParameterSettings] = useState({ starTime: null, toTime: null, fromTime: null, Fr: null, N: null, W: null, DA: null, DP: null })

  const swiperRef = useCallback((ref) => {
    ref.swiper.on('activeIndexChange', (e) => setSelectedItem(e.activeIndex))
  }, [])

  useEffect(() => {
    setShowResynthesisContour(false)
    setResynthesisData(null)
  }, [selectedItem])

  useEffect(() => {
    fetchExercise(id).then((data) => {
      // TODO: Validate data!
      const spec = readSpecification(data)
      setExerciseData(spec)
      setAnnotations(spec.map((item) => item.key.map(() => '')))
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
    if (resynthesisData !== null) {
      const audio = new Audio('data:audio/mpeg;base64,' + resynthesisData.audio)
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
    setAnnotations((a) => R.adjust(itemIndex, R.update(at, val), a))
  }

  function checkAnnotation() {
    // TODO: Nicer equality comparison
    alert(
      `Answer is ${
      R.equals(annotations[selectedItem], exerciseData && exerciseData[selectedItem].key)
          ? 'correct'
          : 'not correct'
      }`
    )
  }

  function showSolution() {
    if (exerciseData !== null) {
      setAnnotations(
        R.update(selectedItem, exerciseData[selectedItem].key, annotations)
      )
    }
  }

  function resynthesize() {
    const { wav, textgrid, blocks, key } = exerciseData[selectedItem]
    const directory = R.nth(-2, location.pathname.split('/'))
    const marks = R.pipe(
      R.reject(R.is(String)),
      R.map(({ choices, index }) =>
        index !== null ? annotations[selectedItem][index] : choices
      )
    )(blocks)

    // The key merged with the preset choices.
    const longKey = R.pipe(
      R.reject(R.is(String)),
      R.reject(({ choices }) => choices === null),
      R.map(({ choices, index }) =>
        index !== null ? key[index] : choices
      )
    )(blocks)

    const error = illegalInputHandling(R.reject(R.isNil, marks), longKey)
    if (error) {
      alert(error)
      return
    }

    const formData = new FormData()
    formData.append('sentence', JSON.stringify(marks))
    formData.append('wav', `${directory}/wav/${wav}`)
    formData.append('TextGrid', `${directory}/TextGrid/${textgrid}`)

    if (customSettingsEnabled) {
      const { starTime, toTime, fromTime, Fr, N, W, DA, DP } = parameterSettings
      if (DP !== null && R.test(/^\d+(\.\d*)?$/, DP)) {
        formData.append('dp', String(DP))
      }
      if (DA !== null && R.test(/^\d+(\.\d*)?$/, DA)) {
        formData.append('da', String(DA))
      }
      if (R.is(Number, fromTime)) {
        formData.append('FROMTIME', String(fromTime))
      }
      if (R.is(Number, toTime)) {
        formData.append('TOTIME', String(toTime))
      }
      if (starTime !== null && R.test(/^\d+(\.\d*)?$/, starTime)) {
        formData.append('STARTIME', String(starTime))
      }
      if (R.is(Number, Fr)) {
        formData.append('Fr', String(Fr))
      }
      if (R.is(Number, N)) {
        formData.append('N', String(N))
      }
      if (R.is(Number, W)) {
        formData.append('W', String(W))
      }
    }

    setResynthesisData(null)
    fetch('/resynthesize/', {
      method: 'POST',
      body: formData,
    })
      .then((r) => r.json())
      .then(setResynthesisData)
  }

  return (
    <div className="App">
      <swiper-container
        ref={swiperRef}
        navigation="true"
        className="exercise-slider"
        effect="fade"
        fade-effect-cross-fade="true"
      >
        {exerciseData !== null &&
          exerciseData.map((item, itemIndex) => (
            <swiper-slide key={itemIndex}>
              <div className="text">
                {item.blocks.map((annotatable, key) =>
                    R.is(String, annotatable) ? (
                      <> {annotatable} </>
                    ) : annotatable.choices === null ? (
                      <> {annotatable.text} </>
                    ) : annotatable.index === null ? (
                      <Annotatable
                        text={annotatable.text}
                        key={key}
                        annotation={annotatable.choices}
                      />
                    ) : (
                      <Annotatable
                        key={key}
                        annotation={annotations[itemIndex][annotatable.index]}
                        options={annotatable.choices}
                        onSelect={updateAnnotation(
                          itemIndex,
                          annotatable.index
                        )}
                        text={annotatable.text}
                      />
                    )
                  )}
              </div>
            </swiper-slide>
          ))}
      </swiper-container>
      <div className="button-container">
        <button onClick={playAudio}>
          Play
        </button>
        <button onClick={toggleContour}>
          {contourVisible ? 'Hide' : 'Show'} contour
        </button>
        <button onClick={checkAnnotation}>Check</button>
        <button onClick={showSolution}>Key</button>
        <button onClick={resynthesize}>Resynthesize</button>
        <button disabled={resynthesisData === null} onClick={playResynthesis}>
          Play resynthesis
        </button>
        <button
          disabled={resynthesisData === null}
          onClick={toggleResynthesisContour}
        >
          {showResynthesisContour ? 'Hide' : 'Show'} resynthesis contour
        </button>
        <button onClick={() => setCustomSettingsEnabled(b => !b)}>
          {customSettingsEnabled ? "Disable" : "Enable"} custom parameters
        </button>
      </div>
      { customSettingsEnabled &&
      <Parameters settings={parameterSettings} onChangeSettings={setParameterSettings} />
      }
      <img
        src={
          exerciseData !== null && selectedItem !== null
            ? `./img/${exerciseData[selectedItem].contour}`
            : undefined
        }
        alt=""
        style={{ width: '100%', display: contourVisible ? 'block' : 'none' }}
      />

      <img
        src={
          resynthesisData !== null
            ? URL.createObjectURL(
                new Blob([resynthesisData.image], { type: 'image/svg+xml' })
              )
            : undefined
        }
        alt=""
        style={{
          width: '100%',
          display:
            showResynthesisContour && resynthesisData !== null
              ? 'block'
              : 'none',
        }}
      />
    </div>
  )
}

export default App
