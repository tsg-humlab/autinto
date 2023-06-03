import * as R from 'ramda'

function parseToken(match, choices) {
  if (match[2]) {
    if (match[2].startsWith('(')) {
      return {
        text: match[1],
        choices: match[2].slice(1, -1), // This drops the surrounding parentheses.
        index: null,
      }
    } else {
      const choicesIndex = Number(match[2])
      return {
        text: match[1],
        choices: choices[choicesIndex],
        index: 0,
      }
    }
  } else {
    return {
      text: match[1],
      choices: null,
      index: null,
    }
  }
}

function assignIndices(tokens) {
  const result = R.mapAccum(
    (index, token) =>
      0 === R.prop('index', token)
        ? [index + 1, { ...token, index: index }]
        : [index, token],
    0,
    tokens
  )
  return result[1]
}

function splitMatches(sentence, regex) {
  const matches = Array.from(sentence.matchAll(regex))
  const chopToken = (start, match) => [
    match.index + match[0].length,
    [sentence.slice(start, match.index), match],
  ]
  const [endOfLastMatch, tokensSoFar] = R.mapAccum(chopToken, 0, matches)
  return R.append(sentence.slice(endOfLastMatch), R.unnest(tokensSoFar))
}

export function parseSentence(sentence, choices) {
  const parsed = splitMatches(sentence, /\[(.*?)\](\d+|\(.*?\))?/g)
    .map((t) => (R.is(Object, t) ? parseToken(t, choices) : t))
    .filter(R.test(/\S/))

  return assignIndices(parsed)
}

export function readSpecification(data) {
  const { items, choices } = data
  return items.map((item) => {
    const { sentence, key, contour, audio, wav, textgrid } = item
    return {
      blocks: parseSentence(sentence, choices),
      key: key,
      contour: contour,
      audio: audio,
      wav,
      textgrid,
    }
  })
}
