import * as R from "ramda"

export function readSpecification(data) {
  const { sentence, choices, key, contour } = data
  const foundMatches = Array.from(sentence.matchAll(/\[(.*?)\](\d+|\(.*?\))/g))
  // Gather all the strings between the matches (i.e. non-annotatable text).
  const inbetweenTexts = R.pipe(
    R.map((match) => [match.index, match.index + match[0].length]),
    R.flatten,
    R.prepend(0),
    R.append(sentence.length),
    R.splitEvery(2),
    R.map(([start, end]) => sentence.substring(start, end))
  )(foundMatches)

  let editableCount = 0
  const annotatables = foundMatches.map((m) => {
    if (m[2].startsWith("(")) {
      // Hardcoded annotation
      return {
        text: m[1],
        choices: m[2].slice(1, -1), // This drops the surrounding parentheses.
        index: null,
      }
    } else {
      // Annotation with choices.
      const choicesIndex = Number(m[2])
      return {
        text: m[1],
        choices: choices[choicesIndex],
        index: editableCount++,
      }
    }
  })

  const combined = R.append(
    R.last(inbetweenTexts),
    R.flatten(R.zip(inbetweenTexts, annotatables))
  )
  return {
    blocks: combined,
    key: key,
    contour: contour,
  }
}
