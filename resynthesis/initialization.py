import parselmouth
import tgt
#from parselmouth.praat import call
from tgt.core import Tier
from tgt.core import TextGrid
import textgrid

sound = parselmouth.Sound("C:/Users/sebas/Documents/Praat-Wavs/test1.wav")

grid = tgt.read_textgrid("C:/Users/sebas/Documents/Praat-Wavs/147.TextGrid")

tg = textgrid.TextGrid.fromFile("C:/Users/sebas/Documents/Praat-Wavs/147.TextGrid")


grid2 = parselmouth.TextGrid.from_tgt(grid)
#print(grid2)

#test1 = call(grid2, "Get number of tiers")
#print(test1)

#test2 = call(grid2, "Get number of intervals", 3)
#print(test2)

vps = (grid.get_tier_by_name("vp"))
ips = (grid.get_tier_by_name("IP's"))

#for x in tester:
    #print(x)
    
#for x in tester2:
    #print(x)

#print(tester[2])

print

# Read a IntervalTier object.
print("------- IntervalTier Example -------")
print(tg[0])
print(tg[0][0])
print(tg[0][0].minTime)
print(tg[0][0].maxTime)
print(tg[0][0].mark)

# Read a PointTier object.
#print("------- PointTier Example -------")
#print(tg[1])
#print(tg[1][0])
#print(tg[1][0].time)
#print(tg[1][0].mark)




#vps zijn altijd om en om en zijn altijd het aantal "Words" dier niet empty is +1



#custom parameters invoegen.
custom = False

#=============================================================================================================================================
#HELPER FUNCTIONS V
#=============================================================================================================================================

#words = {"H*", "!H*", "H*L", "!H*L", "H*LH", "L*H", "L*", "L*HL","L*!HL", "%L", "H%", "%HL", "!%L", "!H%", "!%HL", "L%", "H%", "%"} 
#tones = {H*, !H*, L*, L, H, !H, %L, !%L, H%, !%H, H%, L%}

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
def get_Tvpbegin(indexI, WordList):
    if (indexI == 0 or indexI == len(WordList)-1):
        return
    index = indexI + indexI-1
    return tg[2][index].minTime

#return tvpend using the index on word
def get_Tvpend(indexI, WordList):
    if (indexI == 0 or indexI == len(WordList)-1):
        return
    index = indexI + indexI-1
    return tg[2][index].maxTime

def get_Tipbegin():
    return tg[1][1].minTime

def get_Tipend():
    return tg[1][1].maxTime



#=============================================================================================================================================
#INITIAL FOR LOOP. V
#============================================================================================================================================= 

word = ["%L","L*H","H*L","H*","---","H*L","L*","---","L%"]
tone = [["%L"], ["L*", "H"], ["H*", "L"], ["H*"], [], ["H*", "L"], ["L*"], [], ["L%"]]


if(custom):
    print("hier de code om custom parameters te inputten")
else:
    TOTIME = 90
    FROMTIME = 100
    STARTIME = 0.3  # no longer a time
    da = 0.7
    dp = 0.9
    if(tg[0][0].mark == "v"):
        #print("ITS A WOMAN")
        Fr = 95
        N = 120
        W = 190
    else:
        #print("it ain a woman")
        Fr = 70
        N = 70
        W = 110

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
        print("Tvpbegin:", get_Tvpbegin(i, word))
        print("Tvpend:", get_Tvpend(i, word))
        print("Tipbegin:", get_Tipbegin())
        print("Tipend:", get_Tipend())
        #if (len(nextTone) >= 2):
         #   print(nextTone[0],nextTone[1] )
        print("\n")
        

