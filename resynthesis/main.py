import parselmouth
import textgrid

import parser

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

    script += "Read from file... {}.wav\n".format(file)

    #tone = [["%L"], ["L*", "H"], ["H*", "L"], ["H*"], [], ["H*", "L"], ["L*"], [], ["L%"]]
    tone = make_tone(word)
    print(tone)

    for i in range(len(word)):
        for j in range(len(tone[i])):
            nextWord = next_word2(word, i)
            precWord = prec_word2(word, i)
            nextTone = next_tone2(word, tone, i, j)
            precTone = prec_tone(word, tone, i ,j)

            #First Parse (Final lengtening)
            Tipend = get_Tipend(tg)
            Tvpend = get_Tvpend(i, word, tg)
            Tvpbegin = get_Tvpbegin(i, word, tg)
            if Tipend == Tvpend:
                endtime = Tipend
                vpduur = Tvpend - Tvpbegin
                if (word[i] in ["H*L", "!H*L"] and nextWord in ["H%"]) or (word[i] in ["L*H"] and nextWord in ["L%", "H%", "%"]) or (word[i] in ["L*HL", "L!HL"] and nextWord in ["L%", "%"]):
                    Tipend = endtime - 23 + 11500/vpduur
                    addtime = Tipend - endtime
                    Tvpend = Tipend
            if (word[i] in ["L*HL", "L*!HL"] and nextWord in ["H%"]):
                Tipend = endtime - 23 + 15000/vpduur
                addtime = Tipend - endtime
                Tvpend = Tipend


if __name__ == "__main__":
    word = ["%L","L*H","H*L","H*","---","H*L","L*","---","L%"]
    file = "/home/timon/ToDI/todi-webapp/htdocs/ToDI/ToDIpraat_1a/audio/147"
    run(file, word)
