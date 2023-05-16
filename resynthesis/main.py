import textgrid
import praatparser as parser
import tgt
from tgt.core import TextGrid

#takes the next non-empty word
def next_Word(WordList, IndexI):
    if (IndexI + 1 == len(WordList)):
        return
    else:
        while(WordList[IndexI+1] == "---"):
            IndexI+=1
        return(WordList[IndexI+1])

    
#takes the preceding non-empty word    
def prec_Word(WordList, IndexI):
    if (IndexI <= 0):
        return
    else:
        while(WordList[IndexI-1] == "---"):
            IndexI-=1
        return(WordList[IndexI-1])

#returns the index of the next word
def next_wordI(WordList, IndexI):
    if (IndexI + 1 == len(WordList)):
        return
    else:
        while(WordList[IndexI+1] == "---"):
            IndexI+=1
        return(IndexI+1)

#take next tone and gives i index of next tone(i index related to vp?)     
def next_Tone(WordList, ToneList, IndexI, IndexJ):
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
    index = indexI + indexI-1
    return tg[2][index].minTime

#return tvpend using the index on word
def get_Tvpend(indexI1, WordList, tg, offset):
    indexI = indexI1 - offset
    index = indexI + indexI-1
    return tg[2][index].maxTime

def get_Tipbegin(ipInterval, tg):
    return tg[1][ipInterval].minTime

def get_Tipend(ipInterval, tg):
    return tg[1][ipInterval].maxTime
        

def make_tone(WordList):
    tone = []
    for i in range(len(WordList)):
        if(WordList[i] == "---"):
            tone.append([])
        else:
            tone.append(parser.word_to_tone(WordList[i]))
    return tone

def isBoundary(currentWord):
    Boundaries = ["%L", "%H", "%HL", "!%L", "!%H", "!%HL", "L%", "H%", "%"]
    if(currentWord in Boundaries):
        return True
    else:
        return False
    
def isInitialBoundary(currentWord):
    Boundaries = ["%L", "%H", "%HL", "!%L", "!%H", "!%HL"]
    if(currentWord in Boundaries):
        return True
    else:
        return False

def isFinalBoundary(currentWord):
    Boundaries = ["L%", "H%", "%"]
    if(currentWord in Boundaries):
        return True
    else:
        return False

def createTiers(targetList, TargetTier, FrequencyTier):
    for i in range(len(targetList)):
        time = targetList[i][0]
        label = targetList[i][1]
        frequency = str(targetList[i][2])

        TargetTier.add_point(tgt.core.Point(time, label))
        FrequencyTier.add_point(tgt.core.Point(time, frequency))

def run(file, words):
    script = ""
    grid = tgt.read_textgrid(file + ".TextGrid")
    grid.delete_tiers(["Tones", "Targets", "Frequencies"])
    tgt.io.write_to_file(grid, file + ".TextGrid", format='long')

    tg = textgrid.TextGrid.fromFile(file + ".TextGrid")
    

    tones = make_tone(words)
    tvpOffset = 0
    ipInterval = 0
    targetList = []

    custom = False
    if(custom):
        print("hier de code om custom parameters te inputten")
    else:
        TOTIME = 0.09 
        FROMTIME = 0.10
        STARTIME = 0.30 
        da = 0.7
        dp = 0.9
        if(tg[0][0].mark == "v"):

            Fr = 95
            N = 120
            W = 190
        else:

            Fr = 70
            N = 70
            W = 110
    
    
    WordTier = tgt.core.PointTier(0.0, grid.end_time, "Tones")
    TargetTier = tgt.core.PointTier(0.0, grid.end_time, "Targets")
    FrequencyTier = tgt.core.PointTier(0.0, grid.end_time, "Frequencies")
    grid.add_tiers([WordTier, TargetTier, FrequencyTier])

    for i in range(len(words)):
        
        # Hier wordt en de offset bepaald, en we voegen de word labels toe aan de juiste tier op de juiste plek.
        if(isBoundary(words[i])):
            if isInitialBoundary(words[i]):
                ipInterval+=1
                WordTier.add_point(tgt.core.Point(get_Tipbegin(ipInterval, tg), words[i]))
            else:
                WordTier.add_point(tgt.core.Point(get_Tipend(ipInterval, tg), words[i]))

            if (not i == 0 and not i == len(words)-1):
                tvpOffset+=1
        else:
            WordTier.add_point(tgt.core.Point(get_Tvpbegin(i, words, tg, tvpOffset), words[i]))
        
        for j in range(len(tones[i])):

            word = words[i]
            tone = tones[i][j]
            
            if(isInitialBoundary(word)):
                
                ipbegin = get_Tipbegin(ipInterval, tg)
                Tvp_begin_next = get_Tvpbegin(next_wordI(words, i), words, tg, tvpOffset)
                next_word = next_Word(words, i)

            elif(isFinalBoundary(word)):
                ipend = get_Tipend(ipInterval, tg)
                prec_word = prec_Word(words, i)

            else:
                next_word = next_Word(words, i)
                next_tone = next_Tone(words, tones, i, j)
                ipend = get_Tipend(ipInterval, tg)
                Tvp_begin = get_Tvpbegin(i, words, tg, tvpOffset)
                Tvp_end = get_Tvpend(i, words, tg, tvpOffset)
            
            
            ##########FIRST PARSE: FINAL LENGTHENING for ip-final syllable with many tones
            #FINAL LENGTHENING 1
            #voor drie verschillende tonen
            #moet nog wat beter bekeken worden
            
            # if ipend == Tvpend:
            #     endtime = Tipend
            #     vpduur = Tvpend - Tvp_begin

            #     if (word[i] in ["H*L", "!H*L"] and next_word in ["H%"]) or (word[i] in ["L*H"] and next_word in ["L%", "H%", "%"]) or (word[i] in ["L*HL", "L!HL"] and next_word in ["L%", "%"]):
            #         Tipend = endtime - 0.023 + 11.500/vpduur
            #         addtime = Tipend - endtime
            #         Tvpend = Tipend
            #     if (word[i] in ["L*HL", "L*!HL"] and next_word in ["H%"]):
            #         Tipend = endtime - 0.023 + 15.000/vpduur
            #         addtime = Tipend - endtime
            #         Tvpend = Tipend
                        

            ###########SECOND PARSE: Create aligned and scaled targets.

            freq_low =  Fr + N - (W * 0.5)
            freq_high = Fr + N + (W * 0.5)
            inihigh = freq_high

            #INITIAL BOUNDARY. The rules create the two targets for %L, H% and %HL.

            # To create phrasal downstep
            if tone in ['!']:
                if word in ['!%L', '!%H', '!%HL']:
                    freq_high = Fr + (freq_high - Fr) * dp  
                    freq_low =  Fr + (freq_low - Fr) * dp

            # To create the first target of the initial boundary tone
            if tone in ['%L', '%H']:
                B1time = ipbegin
                if word in ['%L', '!L%']:

                    freq = round(freq_low + 0.3 * W)
                    targetList.append((B1time, "LB1", freq)) # align LB1 B1time ### scale LB1 freq_low + 0.3 * W 
                    
        
                if word in ['%H', '!H%', '%HL', '!%HL']:

                    freq = round(freq_high - 0.15 * W) 
                    targetList.append((B1time, "HB1", freq))

            # To create a second target for (!)%L, (!)%HL and (!)%H, 
            # provided there is a minimal space (here"100 ms) from the beginning of IP to the first pitch accent.
            
            if (word in ["%L", "%H", "%HL", "!%L", "!%H", "!%HL"] and Tvp_begin_next - ipbegin > TOTIME):

                if word in ["%L", "%HL", "!%L", "!%HL"]:

                    if ((Tvp_begin_next) - ipbegin < TOTIME * 2):
                        B2time = ipbegin + (Tvp_begin_next - ipbegin) * 0.5 
                    else:
                        B2time = Tvp_begin_next - TOTIME
                    
                    freq = freq_low + (0.2 * W)
                    targetList.append((B2time, "LB2", freq)) # align LB2 B2time ### scale LB2 freq_low + (0.2 * W)


                if word in ["%H", "!%H"]:

                    if ((Tvp_begin_next - ipbegin) < TOTIME * 2):
                        B2time = ipbegin + (Tvp_begin_next - ipbegin) * 0.5
                    else:
                        B2time = Tvp_begin_next - TOTIME

                    freq = freq_high - (0.3 * W)
                    targetList.append((B2time, "HB2", freq)) # align HB2 B2time ### scale HB2 freq_high - 0.3 * W


            #ACCENTUAL DOWNSTEP
            #The rule lowers the upper and lower boundaries of the pitch range.
    
            if tone in ['!H*', '!H']:
                if word in ['!H*', '!H*L', 'L*!HL']:
                    freq_high = Fr + (freq_high - Fr) * da  
                    freq_low =  Fr + (freq_low - Fr) * da


            #LOW TRAY FOR L*, PLUS DELAYED PEAK
            # This rule creates an extended dip for L*.   #DELAYSPACE TROUBLES?

            if tone in ["L*"]:
                    if word in ["L*", "L*H", "L*HL", "L*!HL"] and next_word in ["L%", "H%", "%"] and (ipend - Tvp_end) < 0.260:
                        
                        delayspace = ipend - Tvp_begin
                        
                        L1time = Tvp_begin - 0.010
                        freq1 = freq_low + 0.2 * W 
                        targetList.append((L1time, "L1", freq1)) #align L1 Tvpbegin - 10 

                        L2time = targetList[-1][0] + 0.010 + delayspace * 0.03
                        freq2 = freq_low + 0.15 * W                   
                        targetList.append((L2time, "L2", freq2)) #align L2 get_time(prec_target) + 10 + delayspace * 0.03

                        L3time = targetList[-1][0] + 0.001 + delayspace * 0.26
                        freq3 = freq_low + 0.15 * W
                        targetList.append((L3time, "L3", freq3)) #align L3 get_time(prec_target) + 1 + delayspace * 0.26


                    elif word in ["L*", "L*H", "L*HL", "L*!HL"] and next_tone in ["H*", "!H*", "L*"] and (Tvp_begin_next - Tvp_end) < 0.360:

                        delayspace = Tvp_begin_next - Tvp_end
                        
                        L1time = Tvp_begin - 0.010
                        freq1 = freq_low + 0.2 * W 
                        targetList.append((L1time, "L1", freq1)) #align L1 Tvpbegin - 10 

                        L2time = targetList[-1][0] + 0.010 + delayspace * 0.03
                        freq2 = freq_low + 0.15 * W                   
                        targetList.append((L2time, "L2", freq2)) #align L2 get_time(prec_target) + 10 + delayspace * 0.03

                        L3time = targetList[-1][0] + 0.001 + delayspace * 0.26
                        freq3 = freq_low + 0.15 * W
                        targetList.append((L3time, "L3", freq3)) #align L3 get_time(prec_target) + 1 + delayspace * 0.26
                        
                    else:

                        delayspace = Tvp_end + 0.360 

                        L1time = Tvp_begin - 0.010 
                        freq1 = freq_low + 0.2 * W 
                        targetList.append((L1time, "L1", freq1)) #align L1 Tvpbegin - 10 

                        L2time = targetList[-1][0] + delayspace * 0.05
                        freq2 = freq_low + 0.15 * W
                        targetList.append((L2time, "L2", freq2)) #align L2 get_time(prec_target) + delayspace * 0.05

                        L3time = targetList[-1][0] + delayspace * 0.7
                        freq3 = freq_low + 0.15 * W 
                        targetList.append((L3time, "L3", freq3)) #align L3 get_time(prec_target) + delayspace * 0.7

            
            # This rule creates a delayed peak after L*
            if tone in ["H", "!H"]:
                    if word in ["L*HL", "L*!HL"] and next_word in ["L%", "H%", "%"] and (ipend - Tvp_end) < 0.260:
                        
                        delayspace = ipend - Tvp_begin

                        H1time = targetList[-1][0] + 0.001 + delayspace * 0.3
                        freq1 = freq_high - 0.3 * W 
                        targetList.append((H1time, "H1", freq1)) #align H1 get_time{prec_target} + 1 + delayspace * 0.3

                        H2time = targetList[-1][0] + delayspace * 0.1
                        freq2 = freq_high - 0.3 * W
                        targetList.append((H2time, "H2", freq2)) #align H2 get_time(prec_target + delayspace * 0.1

                    elif word in ["L*HL", "L*!HL"] and next_tone in ["H*", "!H*", "L*"] and (Tvp_begin_next - Tvp_end) < 0.360:
                            
                        delayspace = Tvp_begin_next - Tvp_end
                        
                        H1time = targetList[-1][0] + 0.001 + delayspace * 0.3
                        freq1 = freq_high - 0.3 * W
                        targetList.append((H1time, "H1", freq1)) #align H1 get_time{prec_target} + 1 + delayspace * 0.3

                        H2time = targetList[-1][0] + delayspace * 0.1
                        freq2 = freq_high - 0.3 * W
                        targetList.append((H2time, "H2", freq2)) #align H2 get_time(prec_target + delayspace * 0.1
                    
                    else:
                        delayspace = Tvp_end + 0.360 

                        H1time = targetList[-1][0] + delayspace * 0.5
                        freq1 = freq_high - 0.3 * W 
                        targetList.append((H1time, "H1", freq1)) #align H1 get_time(prec_target) + delayspace * 0.5

                        H2time = targetList[-1][0] + delayspace * 0.2
                        freq2 = freq_high + 0.3 * W 
                        targetList.append((H2time, "H2", freq2)) #align H2 get_time(prec_target) + delayspace * 0.2


            # FLAT-TOP PEAK
            #This rule creates the alignment and scaling of the first and second targets H* in its vp. 

            if tone in ["H*", "!H*"]:
                if word in ["H*", "H*L", "!H*", "!H*L", "H*LH", "!H*LH"]:
                    
                    vpduur = ipend - Tvp_end
                    freq = freq_high - 0.3 * W

                    if vpduur < 0.250: 

                        H1time = Tvp_begin + (0.4 * STARTIME * vpduur)
                        H2time = H1time + (0.3 * vpduur)

                        targetList.append((H1time, "H1", freq)) #align H1 Htime
                        targetList.append((H2time, "H2", freq)) #align H2 Htime + (0.3 * vpduur)

                    else:
                        vpduur = Tvp_end - Tvp_begin

                        H1time = Tvp_begin + (STARTIME * vpduur)
                        H2time = H1time + (STARTIME * vpduur)

                        targetList.append((H1time, "H1", freq)) #align H1 Htime
                        targetList.append((H2time, "H2", freq)) #align H2 Htime +  (STARTIME * vpduur)


            #PRE-NUCLEAR FALL
            #This rule creates a slow fall before another toneword.
  
            if tone in ["L"]:
                if (word in ["H*L", "!H*L"] ) and (next_tone in ["H*", "!H*", "L*"]):
                    
                    spaceduur = Tvp_begin_next - Tvp_end
                    
                    if spaceduur < TOTIME * 2:

                        ltime = Tvp_begin_next - (spaceduur * 0.5)
                        freq = freq_low + 0.4 * W
                        targetList.append((ltime, "L1", freq)) # align l1 ltime ### scale l1 freq_low + 0.4 * W

                    else:

                        ltime = Tvp_begin_next - TOTIME
                        freq = freq_low - 0.25 * W
                        targetList.append((ltime, "L1", freq))  #align l1 ltime ### scale l1 freq_low - 0.25 * W


            #NUCLEAR FALL
            #This rule creates a fast nuclear fall.
 
            if tone in ["L"]:
                if (word in ["H*L", "L*HL", "!H*L", "L*!HL"]) and (next_word in ["L%", "H%"]):
                    if ipend - targetList[-1][0] < FROMTIME * 2.2:

                        spreadspace = ipend - targetList[-1][0]

                        l1time = targetList[-1][0] + spreadspace * 0.5
                        freq = freq_low + 0.15 * W 
                        targetList.append((l1time, "L1", freq)) # align l1 get_time(prec_target) + spreadtime * 0.5  ### scale l1 freq_low + 0.15 * W

                    else:

                        l1time = targetList[-1][0] + FROMTIME
                        l2time = ipend - TOTIME
                        freq = freq_low + 0.15 * W

                        targetList.append((l1time, "L1", freq)) #align l1 ltime ### scale l1 freq_low + 0.15 * W
                        targetList.append((l2time, "L2", freq)) #align l2 Tipend - TOTIME ### scale l2 freq_low + 0.15 * W

                        
            #PRENUCLEAR RISE AND FALL-RISE
            # This rule creates  the fall from (!)H* in (!)H*LH and the rise from L and L* to the next T*.
            # Creating the fall and the rise
            #BETEKENEN DE GET_TIME(NEXTWORD) HIER DE TVPBEGINS?

            if tone in ["L"]:
                if word in ["H*LH"]:                    
                    if Tvp_begin_next - targetList[-1][0] < FROMTIME * 2:
                        ltime = targetList[-1][0] + (Tvp_begin_next - targetList[-1][0])
                    else:
                        ltime = targetList[-1][0] + TOTIME
                    
                    freq = freq_low + 0.4 * W
                    targetList.append((ltime, "+l", freq)) #align +l ltime ### scale +l freq_low + 0.4 * W
                    

            if tone in ["H"]:
                if word in ["H*LH", "L*H"] and next_tone in ["H*", "!H*", "L*"]:
                    if Tvp_begin_next - targetList[-1][0] < FROMTIME * 2:
                        htime = targetList[-1][0] + (Tvp_begin_next - targetList[-1][0] * 0.5)
                    else:
                        htime = Tvp_begin_next - TOTIME

                    freq = freq_high - 0.3 * W
                    targetList.append((htime, "h1", freq)) #align h1 htime ### scale h1 freq_high - 0.3 * W
                    
                    
                
	

            # #NUCLEAR RISE AND SPREAD FINAL L*, H*, !H*, H, !H of NUCLEAR PITCH ACCENT
            
            if next_word in ["L%", "H%", "%"]:
                if word in ["L*"]:
                    if ipend - Tvp_end > 0.350: #naar ms gezet
                        L4time = targetList[-1][0] + 8
                        l2time = ipend - TOTIME
                        freq = freq_low + 0.2 * W

                        targetList.append((L4time, "L4", freq)) #align L4 get_time prec_target) + 8  ### scale L4 low_freq + 0.2 * W
                        targetList.append((l2time, "l2", freq)) #align l2 Tipend - TOTIME ### scale l2 low_freq + 0.2 * W 


                if word in ["H*", "!H*"]:
                    if ipend - Tvp_end > 0.350: #naar ms gezet
                        H3time = targetList[-1][0] + 8
                        H2time = ipend - TOTIME
                        freq3 = freq_high - 0.33 * W
                        freq2 = freq_high + 0.33 * W

                        targetList.append((H3time, "H3", freq3)) #align H3 get_time prec_target) + 8 ### scale H3 high_freq - 0.33 * W
                        targetList.append((H2time, "h2", freq2)) #align h2 Tipend - TOTIME ### scale h2 high_freq + 0.33 * W

                if tone in ["H"]:
                    if word in ["L*H"]:
                        if ipend - targetList[-1][0] < FROMTIME *2:

                            h1time = targetList[-1][0] + TOTIME * 0.5
                            freq = inihigh - 0.4 * W        
                            targetList.append((h1time, "h1", freq)) #align h1 get_time(prec_target) + FROMTIME ### scale h1 inihigh - 0.4 * W

                        else:
                            
                            h1time = targetList[-1][0] + FROMTIME
                            h2time = ipend - TOTIME
                            freq = inihigh - 0.4 * W

                            targetList.append((h1time, "h1", freq)) #align h1 get_time(prec_target) + FROMTIME ### scale h1 inihigh - 0.4 * W
                            targetList.append((h2time, "h2", freq)) #align h2 Tipend - TOTIME ### scale h2 inihigh - 0.4 * W


            # FINAL BOUNDARY
            # This rule aligns and scales the targets of L%, H% and % at the IP-end. 
            
            if tone in ["L%"]:  
                if word in ["L%"]: 
                    targetList.append((ipend, "LE", freq_low)) #align LE Tipend ### scale LE freq_low
        
            if tone in ["%"]:   
                if word in ["%"]: 
                    if prec_word in ["H*L", "!H*L", "L*HL", "L*!HL"]:  
                        freq = freq_low + W * 0.4
                        targetList.append((ipend, "ME", freq)) #align ME Tipend ### scale ME freq_low + W * 0.4

                    if prec_word in ["H*", "L*H"]:
                        freq = freq_high - W * 0.25 
                        targetList.append((ipend, "ME", freq)) #align ME Tipend ### scale ME freq_high - W * 0.25   

                    if prec_word in ["L*"]:
                        freq = freq_low + W * 0.15
                        targetList.append((ipend, "ME", freq)) #align ME Tipend ### scale ME freq_low + W * 0.15
                
            if tone in ["H%"]:
                if word in ["H%"]:
                    targetList.append((ipend, "HE", inihigh)) #align HE Tipend ### scale LE inihigh
                    
                    


    #print(targetList[-1][0])
    createTiers(targetList, TargetTier, FrequencyTier)    
    tgt.io.write_to_file(grid, file + ".TextGrid", format='long')

if __name__ == "__main__":
    word2 = ["%L","---","H*L","H*","L*", "H*L","L*","---","L%"]
    words = ["%L", "---", "H*L", "---", "---", "---", "---", "---", "L%"]
    #word = ["%L", "---", "---", "---", "H*", "---", "---", "H%", "%L", "---", "---", "H*", "H%"]
    #file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    #file = "C:/Users/sebas/Documents/Software-Engineering/OLD WEBSITE/todi-webapp-master/htdocs/ToDI/ToDIpraat_8a/audio/8a-5"
    run(file, words)
