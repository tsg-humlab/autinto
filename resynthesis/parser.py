#values for testing: 
word = ['H*', '!H*', 'H*L', '!H*L', 'H*LH', 'L*H', 'L*', 'L*HL','L*!HL', '%L', 'H%', '%HL', '!%L', 
'!H%', '!%HL', 'L%', 'H%', '%']
tone = ['H*', '!H*', 'L*', 'L', 'H', '!H', '%L', '!%L', 'H%', '!%H', 'H%', 'L%']


"""I made a couple of assumptions here because some parse rules talk about words or tones that are not in the lists
1: ! alone is not in the list of tones so I made it a seperate item.
2: Sometimes a % and H are swapped (!%H instead of !H%) and these are not both in the list of words so I assumed them to be the same
3: H% is in the list of words twice and I assumed one to be %H and the other to be H%.
4: There is a rule for % -> % but % is not in the list of tones so I added it.
"""

parse =  {word[0]: tone[0],
word[1]:tone[1],
word[2]:[tone[0],tone[3]],
word[3]:[tone[1],tone[3]],
word[4]:[tone[0],tone[3],tone[4]],
word[5]:[tone[2],tone[4]],
word[6]:tone[2],
word[7]:[tone[2],tone[4],tone[3]],
word[8]:[tone[2],tone[1],tone[3]],
word[9]:tone[6],
word[10]:tone[10],
word[11]:[tone[10],tone[6]],
word[12]:['!', tone[6]],
word[13]:['!', tone[10]],
word[14]:['!', tone[10], tone[6]],
word[15]:tone[6],
word[16]:tone[8],
word[17]:'%'}


#returns all the tones associated with a word:
def word_to_tone(word):
	return parse[word]

#returns all the words that translate to a certain tone:
def tone_to_word(tone):
	return [i[0] for i in parse.items() if tone in i[1]]
