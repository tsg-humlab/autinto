import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App"
import "./index.css"

document.querySelectorAll(".exercise").forEach((elem) => {
  const root = createRoot(elem)
  root.render(<App />)
})
