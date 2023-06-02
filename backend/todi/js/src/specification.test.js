import { readSpecification } from './specification'

test('One item specification', () => {
  const spec = readSpecification({
    items: [
      {
        sentence:
          '[](%L) Doe nou maar [gewoon]0 []1 []2 zoals [Willem](!H*L) [](L%)',
        key: ['H*', '\u2205', '\u2205'],
        contour: '2-1.png',
        audio: '2-1.mp3',
        wav: '2-1.wav',
        textgrid: '2-1.TextGrid',
      },
    ],
    choices: [
      [
        ['H*L', '!H*L'],
        ['H*', '!H*'],
        ['H*LH', '\u2205'],
      ],
      [
        ['L%', 'H%'],
        ['%', '\u2205'],
      ],
      [
        ['%L', '%H'],
        ['%HL', '\u2205'],
      ],
    ],
  })

  expect(spec).toEqual([
    {
      blocks: [
        '',
        { text: '', choices: '%L', index: null },
        ' Doe nou maar ',
        {
          text: 'gewoon',
          choices: [
            ['H*L', '!H*L'],
            ['H*', '!H*'],
            ['H*LH', '∅'],
          ],
          index: 0,
        },
        ' ',
        {
          text: '',
          choices: [
            ['L%', 'H%'],
            ['%', '∅'],
          ],
          index: 1,
        },
        ' ',
        {
          text: '',
          choices: [
            ['%L', '%H'],
            ['%HL', '∅'],
          ],
          index: 2,
        },
        ' zoals ',
        { text: 'Willem', choices: '!H*L', index: null },
        ' ',
        { text: '', choices: 'L%', index: null },
        '',
      ],
      key: ['H*', '∅', '∅'],
      contour: '2-1.png',
      audio: '2-1.mp3',
    },
  ])
})
