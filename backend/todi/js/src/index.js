import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App"
import "./index.css"

document.querySelectorAll(".exercise").forEach((elem) => {
  const root = createRoot(elem)
  const id = elem.dataset.exerciseId
  root.render(<App id={id}/>)
})
