export function illegalInputHandling(filledAnnotations, key) {
  let size = filledAnnotations.length

  for (let i = 0; i < size; i++) {
    let annotation = filledAnnotations[i]
    if (annotation == 'H*LH') {
      if (H_star_lh(filledAnnotations, i)) {
        return 'H*LH is a prenuclear pitch accent, meaning that another pitch accent needs to follow in the IP.'
      }
    } else if ((key[i].charAt(0)=='%' || key[i].charAt(0)=='!') && annotation == '') {
      return 'An initial boundary tone is required.'
    } else if (key[i].slice(-1)=='%' && annotation == '') {
      return 'A final boundary tone is required.'
    } else if (
      i == 0 &&
      (annotation == '!%L' || annotation == '!%H' || annotation == '!%HL')
    ) {
      return 'Toelichting labels !%L, !%H, !%HL: these only appear at the beginning of a second IP'
    } else if (annotation == '' && (key[i] == 'L' || key[i] == 'H')) {
      return 'Please fill in a tone. Probably a copy of the last tone of the pitch accent in the preceding IP.'
    }

    if (annotation == '!%L' || annotation == '%L') {
      if (
        filledAnnotations[i + 1] == '!H*' ||
        filledAnnotations[i + 1] == '!HL' ||
        filledAnnotations[i + 1] == 'L*!HL'
      ) {
        return 'Downstepped H-tones normally require a preceding H-tone, at the initial boundary or in a pitch accent'
      }
    }
  }
  if (checkEmptyMedial(filledAnnotations)) {
    return 'Minimally one pitch accent is required.'
  }

  return null
}

function H_star_lh(filledAnnotations, index) {
  let size = filledAnnotations.length

  for (let i = index + 1; i < size; i++) {
    let annotation = filledAnnotations[i]
    if (annotation == '') {
    } else if (annotation.slice(-1) == '%') {
      return true
    } else {
      return false
    }
  }
}

function checkEmptyMedial(filledAnnotations) {
  let size = filledAnnotations.length

  for (let i = 0; i < size; i++) {
    let annotation = filledAnnotations[i]
    if (i != 0 && i != size - 1) {
      if (
        annotation != ''
      ) {
        return false
      }
    }
  }
  return true
}
