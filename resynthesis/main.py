import textgrid
import praatparser as parser
import tgt
from tgt.core import TextGrid


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
def prec_tone2(WordList, ToneList, IndexI, IndexJ):
    if(IndexJ<=0 ):
        if(IndexI <= 0):
            return
        while(WordList[IndexI-1] == "---"):
            IndexI-=1
        return(ToneList[IndexI-1][len(ToneList[IndexI-1])-1])
    else:
        return(ToneList[IndexI][IndexJ-1])    

#returns the index of the next word
def next_wordI(WordList, IndexI):
    if (IndexI + 1 == len(WordList)):
        return
    else:
        while(WordList[IndexI+1] == "---"):
            IndexI+=1
        return(IndexI+1)

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

def get_Tipbegin(bindex, tg):
    return tg[1][bindex].minTime

# def get_Tipend(indexI, WordList, tg, offset):
#     if (indexI == 0):
#         return tg[1][0].maxTime
#     elif (indexI == len(WordList)-1):
#         return tg[1][offset+1].maxTime
#     else:
#         return tg[1][offset].maxTime
        

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
    
def isInitialBoundary(currentWord):
    Boundaries = ["%H", "%L"]
    if(currentWord in Boundaries):
        return True
    else:
        return False

def isFinalBoundary(currentWord):
    Boundaries = ["L%", "H%"]
    if(currentWord in Boundaries):
        return True
    else:
        return False

def run(file, word):
    script = ""
    grid = tgt.read_textgrid(file + ".TextGrid")
    grid.delete_tiers(["Tones", "Targets", "Frequencies"])
    tgt.io.write_to_file(grid, file + ".TextGrid", format='long')

    tg = textgrid.TextGrid.fromFile(file + ".TextGrid")
    

    tone = make_tone(word)
    tvpOffset = 0
    boundaryCounter = 0
    targetList = []

    custom = False
    if(custom):
        print("hier de code om custom parameters te inputten")
    else:
        TOTIME = 0.09 #from miliseconds to seconds
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
    
    
    WordTier = tgt.core.PointTier(0.0, grid.end_time, "Tones")
    TargetTier = tgt.core.PointTier(0.0, grid.end_time, "Targets")
    FrequencyTier = tgt.core.PointTier(0.0, grid.end_time, "Frequencies")
    grid.add_tiers([WordTier, TargetTier, FrequencyTier])


    for i in range(len(word)):
        
        # Hier wordt en de offset bepaald, en we voegen de word labels toe aan de juiste tier op de juiste plek.
        if(isBoundary(word[i])):
            boundaryCounter+=1
            WordTier.add_point(tgt.core.Point(get_Tipbegin(boundaryCounter, tg), word[i]))
            if (not i == 0 and not i == len(word)-1):
                tvpOffset+=1
        else:
            WordTier.add_point(tgt.core.Point(get_Tvpbegin(i, word, tg, tvpOffset), word[i]))
        
        for j in range(len(tone[i])):
            
            #rint(tone[i][j])
            if(isInitialBoundary(word[i])):
                IpTime = get_Tipbegin(boundaryCounter, tg)
                Tvp_begin_next = get_Tvpbegin(next_wordI(word, i), word, tg, tvpOffset)
                next_word = next_word2(word, i)
            elif(isFinalBoundary(word[i])):
                IpTime = get_Tipbegin(boundaryCounter, tg)
                prec_word = prec_word2(word, i)
                next_word = ""
            else:
                next_word = next_word2(word, i)
                next_tone = next_tone2(word, tone, i, j)
                IpTime = get_Tipbegin(boundaryCounter + 1, tg) #voor hier mogelijk +1 omdat we altijd naar de toekomst kijken.
                Tvp_begin = get_Tvpbegin(i, word, tg, tvpOffset)
                Tvp_end = get_Tvpend(i, word, tg, tvpOffset)
            
            
            ###########FIRST PARSE: FINAL LENGTHENING for ip-final syllable with many tones
            #FINAL LENGTHENING 1
            #voor drie verschillende tonen
            #moet nog wat beter bekeken worden
            
            # if IpTime == Tvpend:
            #     endtime = Tipend
            #     vpduur = Tvpend - Tvp_begin

            #     if (word[i] in ["H*L", "!H*L"] and next_word in ["H%"]) or (word[i] in ["L*H"] and next_word in ["L%", "H%", "%"]) or (word[i] in ["L*HL", "L!HL"] and next_word in ["L%", "%"]):
            #         Tipend = endtime - 23 + 11500/vpduur
            #         addtime = Tipend - endtime
            #         Tvpend = Tipend
            #     if (word[i] in ["L*HL", "L*!HL"] and next_word in ["H%"]):
            #         Tipend = endtime - 23 + 15000/vpduur
            #         addtime = Tipend - endtime
            #         Tvpend = Tipend
                        

            ###########SECOND PARSE: Create aligned and scaled targets.

            freq_low =  Fr + N - (W * 0.5)
            freq_high = Fr + N + (W * 0.5)
            inihigh = freq_high

            #INITIAL BOUNDARY. The rules create the two targets for %L, H% and %HL.

            # To create phrasal downstep
            if tone[i][j] in ['!']:
                if word[i] in ['!%L', '!%H', '!%HL']:
                    freq_high = Fr + (freq_high - Fr) * dp  
                    freq_low =  Fr + (freq_low - Fr) * dp

            # To create the first target of the initial boundary tone
            if tone[i][j] in ['%L', '%H']:
                B1time = IpTime
                if word[i] in ['%L', '!L%']:
                    freq = round(freq_low + 0.3 * W) 

                    TargetTier.add_point(tgt.core.Point(B1time, "LB1")) #align LB1 B1time
                    FrequencyTier.add_point(tgt.core.Point(B1time, str(freq))) #scale LB1 freq_low + 0.3 * W 
                    targetList.append((B1time, "LB1"))
                    
        
                if word[i] in ['%H', '!H%', '%HL', '!%HL']:
                    freq = round(freq_high - 0.15 * W) 

                    TargetTier.add_point(tgt.core.Point(B1time, "HB1")) #align HB1 B1time
                    FrequencyTier.add_point(tgt.core.Point(B1time, str(freq))) #scale HB1 freq_high - 0.15 * W
                    targetList.append((B1time, "HB1"))

            # To create a second target for (!)%L, (!)%HL and (!)%H, 
            # provided there is a minimal space (here"100 ms) from the beginning of IP to the first pitch accent.
            
            if (word[i] in ["%L", "%H", "%HL", "!%L", "!%H", "!%HL"] and Tvp_begin_next - IpTime > TOTIME):

                if word[i] in ["%L", "%HL", "!%L", "!%HL"]:

                    if ((Tvp_begin_next) - IpTime < TOTIME * 2):
                        B2time = IpTime + (Tvp_begin_next - IpTime) * 0.5 
                    else:
                        B2time = Tvp_begin_next - TOTIME
                    freq = freq_low + (0.2 * W)

                    TargetTier.add_point(tgt.core.Point(B2time, "LB2")) #align LB2 B2time
                    FrequencyTier.add_point(tgt.core.Point(B2time, str(freq))) #scale LB2 freq_low + (0.2 * W)
                    targetList.append((B2time, "LB2"))


                if word[i] in ["%H", "!%H"]:

                    if ((Tvp_begin_next - IpTime) < TOTIME * 2):
                        B2time = IpTime + (Tvp_begin_next - IpTime) * 0.5
                    else:
                        B2time = Tvp_begin_next - TOTIME
                    freq = freq_high - (0.3 * W)

                    TargetTier.add_point(tgt.core.Point(B2time, "HB2")) #align HB2 B2time
                    FrequencyTier.add_point(tgt.core.Point(B2time, str(freq))) #scale HB2 freq_high - 0.3 * W
                    targetList.append((B2time, "HB2"))


            #ACCENTUAL DOWNSTEP
            #The rule lowers the upper and lower boundaries of the pitch range.
    
            if tone[i][j] in ['!H*', '!H']:
                if word[i] in ['!H*', '!H*L', 'L*!HL']:
                    freq_high = Fr + (freq_high - Fr) * da  
                    freq_low =  Fr + (freq_low - Fr) * da


            #LOW TRAY FOR L*, PLUS DELAYED PEAK
            # This rule creates an extended dip for L*.   #DELAYSPACE TROUBLES?

            if tone[i][j] in ["L*"]:
                    if word[i] in ["L*", "L*H", "L*HL", "L*!HL"]:
                            delayspace = 0 #temp fix
                            if next_word in ["L%", "H%", "%"]:
                                    if (IpTime - Tvp_end) < 0.260: #naar ms gezet
                                        delayspace = IpTime - Tvp_begin
                            if next_tone in ["H*", "!H*", "L*"]:
                                    if (Tvp_begin_next - Tvp_end) < 0.360:
                                        delayspace = Tvp_begin_next - Tvp_end
                        
                            L1time = Tvp_begin - 10 #   KLOPT WSS NIE
                            TargetTier.add_point(tgt.core.Point(L1time, "L1")) #align L1 Tvpbegin - 10 # horen dit 10 ms te zijn?
                            targetList.append((L1time, "L1"))

                            L2time = targetList[-1][0] + 10 + delayspace * 0.03
                            TargetTier.add_point(tgt.core.Point(L2time, "L2")) #align L2 get_time(prec_target) + 10 + delayspace * 0.03
                            targetList.append((L2time, "L2"))

                            L3time = targetList[-1][0] + 1 + delayspace * 0.26
                            TargetTier.add_point(tgt.core.Point(L3time, "L3")) #align L3 get_time(prec_target) + 1 + delayspace * 0.26
                            targetList.append((L3time, "L3"))
                    
                    else:
                        delayspace = Tvp_end + 0.360 #naar ms gezet

                        L1time = Tvp_begin - 10 #   KLOPT WSS NIE
                        freq1 = freq_low + 0.2 * W
                        TargetTier.add_point(tgt.core.Point(L1time, "L1")) #align L1 Tvpbegin - 10 # horen dit 10 ms te zijn?
                        FrequencyTier.add_point(tgt.core.Point(L1time, str(freq1)))
                        targetList.append((L1time, "L1"))

                        L2time = targetList[-1][0] + 10 + delayspace * 0.05
                        freq2 = freq_low + 0.15 * W
                        TargetTier.add_point(tgt.core.Point(L2time, "L2")) #align L2 get_time(prec_target) + delayspace * 0.05
                        FrequencyTier.add_point(tgt.core.Point(L2time, str(freq2))) 
                        targetList.append((L2time, "L2"))

                        L3time = targetList[-1][0] + 1 + delayspace * 0.26
                        freq3 = freq_low + 0.15 * W
                        TargetTier.add_point(tgt.core.Point(L3time, "L3")) #align L3 get_time(prec_target) + delayspace * 0.7
                        FrequencyTier.add_point(tgt.core.Point(L3time, str(freq3)))
                        targetList.append((L3time, "L3"))

            
            # This rule creates a delayed peak after L*
            if tone[i][j] in ["H", "!H"]:
                    if word[i] in ["L*HL", "L*!HL"]:
                            delayspace = 0 #temp fix
                            if next_word in ["L%", "H%", "%"]:
                                    if (IpTime - Tvp_end) < 0.260: #naar ms gezet
                                        delayspace = IpTime - Tvp_begin
                            if next_tone in ["H*", "!H*", "L*"]:
                                    if (Tvp_begin_next - Tvp_end) < 0.360:
                                        delayspace = Tvp_begin_next - Tvp_end
                        
                            H1time = targetList[-1][0] + 1 + delayspace * 0.3
                            freq1 = freq_high - 0.3 * W
                            TargetTier.add_point(tgt.core.Point(H1time, "H1")) #align H1 get_time{prec_target} + 1 + delayspace * 0.3
                            FrequencyTier.add_point(tgt.core.Point(H1time, str(freq1)))
                            targetList.append((H1time, "H1"))

                            H2time = targetList[-1][0] + delayspace * 0.1
                            freq2 = freq_high - 0.3 * W
                            TargetTier.add_point(tgt.core.Point(H2time, "H2")) #align H2 get_time(prec_target + delayspace * 0.1
                            FrequencyTier.add_point(tgt.core.Point(H2time, str(freq2)))
                            targetList.append((H2time, "H2"))
                    
                    else:
                        delayspace = Tvp_end + 0.360 #naar ms gezet

                        H1time = targetList[-1][0] + delayspace * 0.5
                        freq1 = freq_high - 0.3 * W
                        TargetTier.add_point(tgt.core.Point(H1time, "H1")) #align H1 get_time(prec_target) + delayspace * 0.5
                        FrequencyTier.add_point(tgt.core.Point(H1time, str(freq1)))
                        targetList.append((H1time, "H1"))

                        H2time = targetList[-1][0] + delayspace * 0.2
                        freq2 = freq_high - 0.3 * W
                        TargetTier.add_point(tgt.core.Point(H2time, "H2")) #align H2 get_time(prec_target) + delayspace * 0.2
                        FrequencyTier.add_point(tgt.core.Point(H2time, str(freq2)))
                        targetList.append((H2time, "H2"))


            # FLAT-TOP PEAK
            #This rule creates the alignment and scaling of the first and second targets H* in its vp. 

            if tone[i][j] in ["H*", "!H*"]:
                if word[i] in ["H*", "H*L", "!H*", "!H*L", "H*LH", "!H*LH"]:
                    vpduur = IpTime - Tvp_end
                    if vpduur < 0.250: #naar ms gezet
                        H1time = Tvp_begin + (0.4 * STARTIME * vpduur)
                        H2time = H1time + (0.3 * vpduur)
                        TargetTier.add_point(tgt.core.Point(H1time, "H1")) #align H1 Htime
                        targetList.append((H1time, "H1"))
                        TargetTier.add_point(tgt.core.Point(H2time, "H2")) #align H2 Htime + (0.3 * vpduur)
                        targetList.append((H2time, "H2"))

                    else:
                        vpduur = Tvp_end - Tvp_begin
                        H1time = Tvp_begin + (STARTIME * vpduur)
                        H2time = H1time + (STARTIME * vpduur)
                        TargetTier.add_point(tgt.core.Point(H1time, "H1")) #align H1 Htime
                        targetList.append((H1time, "H1"))
                        TargetTier.add_point(tgt.core.Point(H2time, "H1")) #align H2 Htime +  (STARTIME * vpduur)
                        targetList.append((H2time, "H2"))
                
                freq = freq_high - 0.3 * W
                FrequencyTier.add_point(tgt.core.Point(H1time, str(freq))) #scale H1 freq_high - 0.3 * W	
                FrequencyTier.add_point(tgt.core.Point(H2time, str(freq))) #scale H2 freq_high - 0.3 * W


            #PRE-NUCLEAR FALL
            #This rule creates a slow fall before another toneword.
  
            if tone[i][j] in ["L"]:
                if (word[i] in ["H*L", "!H*L"] ) and (next_tone in ["H*", "!H*", "L*"]):
                    spaceduur = Tvp_begin_next - Tvp_end
                    if spaceduur < TOTIME * 2:
                        ltime = Tvp_begin_next - (spaceduur * 0.5)
                        freq = freq_low + 0.4 * W
                        TargetTier.add_point(tgt.core.Point(ltime, "L1")) #align l1 ltime
                        targetList.append((ltime, "L1"))
                        FrequencyTier.add_point(tgt.core.Point(ltime, str(freq))) #scale l1 freq_low + 0.4 * W
                    else:
                        ltime = Tvp_begin_next - TOTIME
                        freq = freq_low - 0.25 * W
                        TargetTier.add_point(tgt.core.Point(ltime, "L1")) #align l1 ltime
                        targetList.append((ltime, "L1"))
                        FrequencyTier.add_point(tgt.core.Point(ltime, str(freq))) #scale l1 freq_low - 0.25 * W




            #NUCLEAR FALL
            #This rule creates a fast nuclear fall.
 
            if tone[i][j] in ["L"]:
                if (word[i] in ["H*L", "L*HL", "!H*L", "L*!HL"]) and (next_word in ["L%", "H%"]):
                    if IpTime - targetList[-1][0] < FROMTIME * 2.2:
                        spreadspace = IpTime - targetList[-1][0]
                        l1time = targetList[-1][0] + spreadspace * 0.5
                        TargetTier.add_point(tgt.core.Point(l1time, "L1")) #align l1 get_time(prec_target) + spreadtime * 0.5
                        targetList.append((l1time, "L1"))
                        #align l1 ltime #NOT SURE WAT HIER MOET GEBEUREN
                    else:
                        l1time = targetList[-1][0] + FROMTIME
                        l2time = IpTime - TOTIME
                        TargetTier.add_point(tgt.core.Point(l1time, "L1")) #align l1 ltime
                        targetList.append((l1time, "L1"))
                        TargetTier.add_point(tgt.core.Point(l2time, "L2")) #align l2 Tipend - TOTIME
                        targetList.append((l2time, "L2"))
                        
                    freq = freq_low + 0.15 * W
                    FrequencyTier.add_point(tgt.core.Point(l1time, str(freq))) #scale l1 freq_low + 0.15 * W
                    FrequencyTier.add_point(tgt.core.Point(l2time, str(freq))) #scale l2 freq_low + 0.15 * W



            #PRENUCLEAR RISE AND FALL-RISE
            # This rule creates  the fall from (!)H* in (!)H*LH and the rise from L and L* to the next T*.
            # Creating the fall and the rise
            #BETEKENEN DE GET_TIME(NEXTWORD) HIER DE TVPBEGINS?

            if tone[i][j] in ["L"]:
                if word[i] in ["H*LH"]:                    
                    if Tvp_begin_next - targetList[-1][0] < FROMTIME * 2:
                        ltime = targetList[-1][0] + (Tvp_begin_next - targetList[-1][0])
                    else:
                        ltime = targetList[-1][0] + TOTIME
                    
                    TargetTier.add_point(tgt.core.Point(ltime, "+l")) #align +l ltime
                    targetList.append((ltime, "+l"))
                    freq = freq_low + 0.4 * W
                    FrequencyTier.add_point(tgt.core.Point(ltime, str(freq))) #scale +l freq_low + 0.4 * W

            if tone[i][j] in ["H"]:
                if word[i] in ["H*LH", "L*H"] and next_tone in ["H*", "!H*", "L*"]:
                    if Tvp_begin_next - targetList[-1][0] < FROMTIME * 2:
                        htime = targetList[-1][0] + (Tvp_begin_next - targetList[-1][0] * 0.5)
                    else:
                        htime = Tvp_begin_next - TOTIME

                    TargetTier.add_point(tgt.core.Point(htime, "h1")) #align h1 htime
                    targetList.append((htime, "h1"))
                    freq = freq_high - 0.3 * W
                    FrequencyTier.add_point(tgt.core.Point(htime, str(freq))) #scale h1 freq_high - 0.3 * W
                
	

            # #NUCLEAR RISE AND SPREAD FINAL L*, H*, !H*, H, !H of NUCLEAR PITCH ACCENT
            
            if next_word in ["L%", "H%", "%"]:
                if word[i] in ["L*"]:
                    if IpTime - Tvp_end > 0.350: #naar ms gezet
                        L4time = targetList[-1][0] + 8
                        l2time = IpTime - TOTIME
                        freq = freq_low + 0.2 * W

                        TargetTier.add_point(tgt.core.Point(L4time, "L4")) #align L4 get_time prec_target) + 8
                        targetList.append((L4time, "L4"))

                        TargetTier.add_point(tgt.core.Point(l2time, "l2")) #align l2 Tipend - TOTIME
                        targetList.append((l2time, "l2"))

                        FrequencyTier.add_point(tgt.core.Point(L4time, str(freq))) # scale L4 low_freq + 0.2 * W
                        FrequencyTier.add_point(tgt.core.Point(l2time, str(freq))) # scale l2 low_freq + 0.2 * W 

                if word[i] in ["H*", "!H*"]:
                    if IpTime - Tvp_end > 0.350: #naar ms gezet
                        H3time = targetList[-1][0] + 8
                        H2time = IpTime - TOTIME
                        freq3 = freq_high - 0.33 * W
                        freq2 = freq_high + 0.33 * W

                        TargetTier.add_point(tgt.core.Point(H3time, "H3")) #align H3 get_time prec_target) + 8
                        targetList.append((H3time, "H3"))

                        TargetTier.add_point(tgt.core.Point(H2time, "h2")) #align h2 Tipend - TOTIME
                        targetList.append((H2time, "h2"))

                        FrequencyTier.add_point(tgt.core.Point(H3time, str(freq3))) # scale H3 high_freq - 0.33 * W
                        FrequencyTier.add_point(tgt.core.Point(H2time, str(freq2))) # scale h2 high_freq + 0.33 * W

                if tone[i][j] in ["H"]:
                    if word[i] in ["L*H"]:
                        if IpTime - targetList[-1][0] < FROMTIME *2:
                            TEST =0 #WAT GEBEURT HIER IN DE PSEUDO/MIST ER IETS?
                        else:
                            h1time = targetList[-1][0] + FROMTIME
                            h2time = IpTime - TOTIME

                            TargetTier.add_point(tgt.core.Point(h1time, "h1")) #align h1 get_time(prec_target) + FROMTIME
                            targetList.append((h1time, "h1"))

                            TargetTier.add_point(tgt.core.Point(h2time, "h2")) #align h2 Tipend - TOTIME
                            targetList.append((h2time, "h2"))

                    freq = inihigh - 0.4 * W
                    FrequencyTier.add_point(tgt.core.Point(h1time, str(freq))) # scale h1 inihigh - 0.4 * W
                    FrequencyTier.add_point(tgt.core.Point(H2time, str(freq))) # scale h2 inihigh - 0.4 * W


            # FINAL BOUNDARY
            # This rule aligns and scales the targets of L%, H% and % at the IP-end. 
            
            if tone[i][j] in ["L%"]:  
                if word[i] in ["L%"]: 
                    TargetTier.add_point(tgt.core.Point(IpTime, "LE")) #align LE Tipend
                    targetList.append((IpTime, "LE"))                    
                    FrequencyTier.add_point(tgt.core.Point(IpTime, str(freq_low))) #scale LE freq_low
        
            if tone[i][j] in ["%"]:   
                if word[i] in ["%"]:
                    
                    TargetTier.add_point(tgt.core.Point(IpTime, "ME")) #align ME Tipend
                    targetList.append((IpTime, "ME"))
                    
                    if prec_word in ["H*L", "!H*L", "L*HL", "L*!HL"]:  
                        freq = freq_low + W * 0.4
                        FrequencyTier.add_point(tgt.core.Point(IpTime, str(freq))) #scale ME freq_low + W * 0.4

                    if prec_word in ["H*", "L*H"]:
                        freq = freq_high - W * 0.25 
                        FrequencyTier.add_point(tgt.core.Point(IpTime, str(freq))) #scale ME freq_high - W * 0.25   

                    if prec_word in ["L*"]:
                        freq = freq_low + W * 0.15
                        FrequencyTier.add_point(tgt.core.Point(IpTime, str(freq))) #scale ME freq_low + W * 0.15
                
            if tone[j] in ["H%"]:
                if word[i] in ["H%"]:
                    TargetTier.add_point(tgt.core.Point(IpTime, "HE")) #align HE Tipend
                    targetList.append((IpTime, "HE"))
                    FrequencyTier.add_point(tgt.core.Point(IpTime, str(inihigh))) 
                    
                    


    #print(targetList[-1][0])    
    tgt.io.write_to_file(grid, file + ".TextGrid", format='long')

if __name__ == "__main__":
    word = ["%L","---","H*L","H*","L*", "H*L","L*","---","L%"]
    word2 = ["%L", "---", "H*L", "---", "---", "---", "---", "---", "L%"]
    #word = ["%L", "---", "---", "---", "H*", "---", "---", "H%", "%L", "---", "---", "H*", "H%"]
    #file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    file = "C:/Users/sebas/Documents/Praat-Wavs/147"
    #file = "C:/Users/sebas/Documents/Software-Engineering/OLD WEBSITE/todi-webapp-master/htdocs/ToDI/ToDIpraat_8a/audio/8a-5"
    run(file, word)
