import parselmouth
import textgrid
import praatparser as parser

#takes the next word even if empty
def next_word(WordList, IndexI):
    if (IndexI + 1 == len(WordList)):
        return
    else:
        return(WordList[IndexI+1])

#takes the next non-empty word
def next_word2(WordList, IndexI):
    if (IndexI + 1 == len(WordList)):
        return
    else:
        while(WordList[IndexI+1] == "---"):
            IndexI+=1
        return(WordList[IndexI+1])
    
#takes the preceding word even if empty    
def prec_word(WordList, IndexI):
    if (IndexI <= 0):
        return
    else:
        return(WordList[IndexI-1])
    
#takes the preceding non-empty word    
def prec_word2(WordList, IndexI):
    if (IndexI <= 0):
        return
    else:
        while(WordList[IndexI-1] == "---"):
            IndexI-=1
        return(WordList[IndexI-1])
    
#takes the next tone
def next_tone(WordList, ToneList, IndexI, IndexJ):
    if(IndexJ+1 == len(ToneList[IndexI])):
        if(IndexI + 1 == len(WordList)):
            return
        while(WordList[IndexI+1] == "---"):
            IndexI+=1
        return(ToneList[IndexI+1][0])
    else:
        return(ToneList[IndexI][IndexJ+1])
    
#takes previous tone
def prec_tone(WordList, ToneList, IndexI, IndexJ):
    if(IndexJ<=0 ):
        if(IndexI <= 0):
            return
        while(WordList[IndexI-1] == "---"):
            IndexI-=1
        return(ToneList[IndexI-1][len(ToneList[IndexI-1])-1])
    else:
        return(ToneList[IndexI][IndexJ-1])    

#take next tone and gives i index of next tone(i index related to vp?)     
def next_tone2(WordList, ToneList, IndexI, IndexJ):
    if(IndexJ+1 == len(ToneList[IndexI])):
        if(IndexI + 1 == len(WordList)):
            return("")
        while(WordList[IndexI+1] == "---"):
            IndexI = IndexI + 1
        return(ToneList[IndexI+1][0], IndexI+1)
    else:
        return(ToneList[IndexI][IndexJ+1], IndexI)
    
    
#return tvpbegin using the index on word    
def get_Tvpbegin(indexI, WordList, tg):
    if (indexI == 0 or indexI == len(WordList)-1):
        return
    index = indexI + indexI-1
    return tg[2][index].minTime

#return tvpend using the index on word
def get_Tvpend(indexI, WordList, tg):
    if (indexI == 0 or indexI == len(WordList)-1):
        return
    index = indexI + indexI-1
    return tg[2][index].maxTime

def get_Tipbegin(tg):
    return tg[1][1].minTime

def get_Tipend(tg):
    return tg[1][1].maxTime

def make_tone(WordList):
    tone = []
    for i in range(len(WordList)):
        if(WordList[i] == "---"):
            tone.append([])
        else:
            tone.append(parser.word_to_tone(WordList[i]))
    return tone


def run(file, word):
    script = ""
    tg = textgrid.TextGrid.fromFile(file + ".TextGrid")

    #script += "Read from file... {}.wav\n".format(file)

    #tone = [["%L"], ["L*", "H"], ["H*", "L"], ["H*"], [], ["H*", "L"], ["L*"], [], ["L%"]]
    tone = make_tone(word)
    print(tone)

    for i in range(len(word)):
        for j in range(len(tone[i])):
            nextWord = next_word2(word, i)
            precWord = prec_word2(word, i)
            nextTone = next_tone2(word, tone, i, j)
            precTone = prec_tone(word, tone, i ,j)

            print("Word to work with:", word[i]) 
            print("Tone to work with:", tone[i][j])
            print("Next word:", nextWord)
            print("Previous word:", precWord)
            print("Next tone:", nextTone)
            print("previous tone:", precTone)
            print("Tvpbegin:", get_Tvpbegin(i, word, tg))
            print("Tvpend:", get_Tvpend(i, word, tg))
            print("Tipbegin:", get_Tipbegin(tg))
            print("Tipend:", get_Tipend(tg))
            #if (len(nextTone) >= 2):
             #   print(nextTone[0],nextTone[1] )
            print("\n")


if __name__ == "__main__":
    word = ["%L","L*H","H*L","H*","---","H*L","L*","---","L%"]
    file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    run(file, word)
