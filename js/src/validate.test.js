import { illegalInputHandling } from './validate'

test('Minimally one pitch accent is required.', () => {
  const error = illegalInputHandling(['%', '', '', '%'], ['%', '', '', '%'])

  expect(error).toEqual('Minimally one pitch accent is required.')
})

test('Downstepped H-tones normally require a preceding H-tone, at the initial boundary or in a pitch accent', () => {
  const error = illegalInputHandling(
    ['%', '!%L', '!H*', '%'],
    ['%', '!%L', '!H*', '%']
  )

  expect(error).toEqual(
    'Downstepped H-tones normally require a preceding H-tone, at the initial boundary or in a pitch accent'
  )
})

test('Toelichting labels !%L, !%H, !%HL: these only appear at the beginning of a second IP', () => {
  const error = illegalInputHandling(['!%L', '', 'k'], ['!%L', '', 'k'])

  expect(error).toEqual(
    'Toelichting labels !%L, !%H, !%HL: these only appear at the beginning of a second IP'
  )
})
test('A final boundary tone is required.', () => {
  const error = illegalInputHandling(['%L', '', ''], ['%L', '', ''])

  expect(error).toEqual('A final boundary tone is required.')
})

test('An initial boundary tone is required.', () => {
  const error = illegalInputHandling(['', '', 'H%'], ['', '', 'H%'])

  expect(error).toEqual('An initial boundary tone is required.')
})

test('H*LH is a prenuclear pitch accent, meaning that another pitch accent needs to  follow in the IP.', () => {
  const error = illegalInputHandling(
    ['%', 'H*LH', '', '%'],
    ['%', 'H*LH', '', '%']
  )

  expect(error).toEqual(
    'H*LH is a prenuclear pitch accent, meaning that another pitch accent needs to follow in the IP.'
  )
})

test('Please fill in a tone. Probably a copy of the last tone of the pitch accent in the preceding IP.', () => {
  const error = illegalInputHandling(
    ['%', '%H', 'H', '%'],
    ['%', '%H', 'H', '%']
  )

  expect(error).toEqual(
    'Please fill in a tone. Probably a copy of the last tone of the pitch accent in the preceding IP.'
  )
})

test('Correct example 1', () => {
  const error = illegalInputHandling(
    ['%', 'H*LH', 'H*LH', '%'],
    ['%', 'H*LH', 'H*LH', '%']
  )

  expect(error).toEqual(null)
})

test('Minimally one pitch accent is required.', () => {
  const error = illegalInputHandling(['%', '', '', '%'], ['%', '', '', '%'])

  expect(error).toEqual('Minimally one pitch accent is required.')
})

test('Downstepped H-tones normally require a preceding H-tone, at the initial boundary or in a pitch accent', () => {
  const error = illegalInputHandling(
    ['%', '!%L', '!H*', '%'],
    ['%', '!%L', '!H*', '%']
  )

  expect(error).toEqual(
    'Downstepped H-tones normally require a preceding H-tone, at the initial boundary or in a pitch accent'
  )
})

test('Toelichting labels !%L, !%H, !%HL: these only appear at the beginning of a second IP', () => {
  const error = illegalInputHandling(['!%L', '', 'k'], ['!%L', '', 'k'])

  expect(error).toEqual(
    'Toelichting labels !%L, !%H, !%HL: these only appear at the beginning of a second IP'
  )
})

test('A final boundary tone is required', () => {
  const error = illegalInputHandling(['%L', '', ''], ['%L', '', ''])

  expect(error).toEqual('A final boundary tone is required.')
})

test('An initial boundary tone is required.', () => {
  const error = illegalInputHandling(['', '', 'H%'], ['', '', 'H%'])

  expect(error).toEqual('An initial boundary tone is required.')
})

test('H*LH is a prenuclear pitch accent, meaning that another pitch accent needs to  follow in the IP.', () => {
  const error = illegalInputHandling(
    ['%', 'H*LH', '', '%'],
    ['%', 'H*LH', '', '%']
  )

  expect(error).toEqual(
    'H*LH is a prenuclear pitch accent, meaning that another pitch accent needs to follow in the IP.'
  )
})

test('Please fill in a tone. Probably a copy of the last tone of the pitch accent in the preceding IP.', () => {
  const error = illegalInputHandling(
    ['%', '%H', 'H', '%'],
    ['%', '%H', 'H', '%']
  )

  expect(error).toEqual(
    'Please fill in a tone. Probably a copy of the last tone of the pitch accent in the preceding IP.'
  )
})

test('Correct example 2', () => {
  const error = illegalInputHandling(
    ['%', 'H*LH', 'H*LH', '%'],
    ['%', 'H*LH', 'H*LH', '%']
  )

  expect(error).toEqual(null)
})
