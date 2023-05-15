#parse rules:
parse = {'%L': ['%L'],
'%H': ['%H'],
'%HL': ['%H','%L'],
'!%L': ['!','%L'],
'!%H': ['!','%H'],
'!%HL': ['!','%H','%L'],
'H*': ['H*'],
'!H*': ['!H*'],
'H*L': ['H*','L'],
'!H*L': ['!H*','L'],
'H*LH': ['H*','L','H'],
'L*': ['L*'],
'L*H': ['L*','H'],
'L*HL': ['L*','H','L'],
'L*!HL': ['L*','!H','L'],
'L%': ['L%'],
'H%': ['H%'],
'%': ['%']
}


#returns all the tones associated with a word:
def word_to_tone(word):
	return parse[word]


#returns all the words that translate to a certain tone:
def tone_to_word(tone):
	return [i[0] for i in parse.items() if tone in i[1]]
