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
def get_Tvpbegin(indexI1, WordList, tg, offset):
    indexI = indexI1 - offset
    if (indexI == 0 or indexI == len(WordList)-1):
        return 0
    index = indexI + indexI-1
    return tg[2][index].minTime

#return tvpend using the index on word
def get_Tvpend(indexI1, WordList, tg, offset):
    indexI = indexI1 - offset
    if (indexI == 0 or indexI == len(WordList)-1):
        return 0
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

def isBoundary(currentWord):
    Boundaries = ["%H", "%L", "L%", "H%"]
    if(currentWord in Boundaries):
        return True
    else:
        return False



def run(file, word):
    script = ""
    tg = textgrid.TextGrid.fromFile(file + ".TextGrid")

    #script += "Read from file... {}.wav\n".format(file)

    #tone = [["%L"], ["L*", "H"], ["H*", "L"], ["H*"], [], ["H*", "L"], ["L*"], [], ["L%"]]
    tone = make_tone(word)
    #print(tone)

    tvpOffset = 0

    custom = False
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
            
            if(isBoundary(word[i])):
                if (not i == 0 and not i == len(word)-1):
                    tvpOffset+=1

            nextWord = next_word2(word, i)
            precWord = prec_word2(word, i)
            nextTone = next_tone2(word, tone, i, j)
            precTone = prec_tone(word, tone, i ,j)

            #First Parse (Final lengtening)
            Tipend = get_Tipend(tg)
            if (i == 0 or i == len(word)-1):
                #temporary, eigenlijk mag tvpend en begin niet op n boundary tone gecalled worden
                #dit is namelijk ook nooit nodig.
                Tvpend = 0
                Tvpbegin = 0
            else:
                Tvpend = get_Tvpend(i, word, tg, tvpOffset)
                Tvpbegin = get_Tvpbegin(i, word, tg, tvpOffset)
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

            ###########SECOND PARSE: Create aligned and scaled targets.

            freq_low =  Fr + N - (W * 0.5)
            freq_high = Fr + N + (W * 0.5)
            inihigh = freq_high

            #INITIAL BOUNDARY. The rules create the two targets for %L, H% and %HL.

            if tone in ['!']:
                if word in ['!%L', '!%H', '!%HL']:
                    freq_high = Fr + (freq_high - Fr) * dp  
                    freq_low =  Fr + (freq_low - Fr) * dp

            if tone in ['%L', '%H']:
                if word in ['%L', '!L%']:
                    B1time = Tipbegin
                    #align LB1 B1time
                    #scale LB1 freq_low + 0.3 * W 
        
                if word in ['%H', '!H%', '%HL', '!%HL']:
                    B1time = Tipbegin
                    #align HB1 B1time
                    #scale HB1 freq_high - 0.15 * W

            if tone in ['%L']:
                if word in ['L%', '%HL'] and (next_tone in ['!H*', 'H*', 'L*']) and (get_Tvpbegin(next_tone) - Tipbegin) < TOTIME * 2:
                    B2time = Tipbegin + (get_Tvpbegin(next_tone) - Tipbegin) * 0.5 
                else:
                    B2time = get_Tvpbegin(next_tone) - TOTIME
                    #align LB2 B2time
                    #scale LB2 freq_low + (0.2 * W)

            if tone in ['%H']:
                if (word in ['%H']) and (next_tone in ['!H*', 'H*', 'L*']) and (get_Tvpbegin(next_tone) - Tipbegin) < TOTIME * 2:
                    B2time = Tipbegin + (get_Tvpbegin(next_tone) - Tipbegin) * 0.5 
                else:
                    B2time = get_Tvpbegin(next_tone) - TOTIME
                    #align HB2 B2time
                    #scale HB2 freq_high - 0.3 * W

            #ACCENTUAL DOWNSTEP
            #The rule lowers the upper and lower boundaries of the pitch range.
    
            if tone in ['!H*', '!H']:
                if word in ['!H*', '!H*L', 'L*!HL']:
                    freq_high = Fr + (freq_high - Fr) * da  
                    freq_low =  Fr + (freq_low - Fr) * da

            # FLAT-TOP PEAK
            #This rule creates the alignment and scaling of the first and second targets H* in its vp. 

            if tone in ['H*', '!H*']:
                if word in ['H*', 'H*L', '!H*', '!H*L']:
                    vpduur = Tipend - Tvpbegin
                    if vpduur < 200:
                        Htime = Tvpbegin + (0.4 * STARTIME * vpduur)
                    else:
                        Htime = Tvpbegin + (STARTIME * vpduur)
                    #align H1 Htime
                    #align H2 Htime + (0.6 * vpduur)
                    #scale H1 freq_high - 0.3 * W    
                    #scale H2 freq_high - 0.3 * W

            #PRE-NUCLEAR FALL
            #This rule creates a slow fall before another toneword.
  
            if tone in ['L']:
                if (word in ['H*L', 'L*HL', '!H*L', 'L*!HL']) and (next_tone in ['H*', '!H*', 'L*']):
                    spaceduur = get_Tvpbegin(next_tone) - get_Tvpend(prec_tone)
                    if spaceduur < TOTIME * 2:
                        ltime = get_Tvpbegin(next_tone) - (spaceduur * 0.5)
                        #align l1 ltime
                        #scale l1 freq_low + 0.4 * W
                    else:
                        ltime = get_Tvbegin(next_tone) - TOTIME
                        #align l1 ltime
                        #scale l1 freq_low - 0.25 * W

            #NUCLEAR FALL
            #This rule creates a fast nuclear fall.
 
            if tone in ['L']:
                if (word in ['H*L', 'L*HL', '!H*L', 'L*!HL']) and (next_word in ['L%'], ['H%']):
                    if Tipend - time(prec_tone) < TOTIME:
                        ltime = time(prec_tone) + (Tipend - time(prec_label) * 0.5)
                    else:
                        ltime = time(prec_tone) + FROMTIME
                        #align l1 ltime
                        #scale l1 freq_low + 0.9 * W
                        #align l2 Tipend - TOTIME
                        #scale l2 freq_low + 0.9 * W
  
            # FINAL BOUNDARY
            # This rule aligns and scales the targets of L%, H% and % at the IP-end. 
            
            if tone in ['L%']:  
                if word in ['L%']: 
                    etime = Tipend
                    #align LE etime
                    #scale LE freq_low
        
            if tone in ['%']:   
                if word in ['%']:
                    etime = Tipend
                    #align ME etime
                    #if prec_word in ['H*L', '!H*L', 'L*HL', 'L*!HL']:  
                        #scale ME freq_low + W * 0.4
                    #if prec_word in ['H*', 'L*H']:
                        #scale ME freq_high - W * 0.25   
                    #if prec_word in ['L*']:
                        #scale ME freq_low + W * 0.15
                
            if tone in ['H%']:
                if word in ['H%']:
                    etime = Tipend
                    #align HE etime
                    #scale HE freq_inihigh
        
     

if __name__ == "__main__":
    word = ["%L","L*H","H*L","H*","L*", "H%", "H%" , "H*L","L*","---","L%"]
    #file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    file = "/home/pim/Documents/todi/147"
    run(file, word)
