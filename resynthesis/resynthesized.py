from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from functools import cached_property
import copy
from datetime import timedelta

import textgrid as tg

from resynthesis.phrase import Phrase, IntonationalPhrase
from resynthesis.pitch_accents import Word, InitialBoundary, FinalBoundary
from resynthesis.types import ResynthesizeVariables, FrequencyRange, FrequencyPoint, AddTime


@dataclass
class ResynthesizedIntonationalPhrase:
    """
    A part of the ResynthesizedPhrase, this class represents an IP to be
    resynthesized. It stores the pitch accents in an IP of the resynthesis
    request, and the VoicedPortions of those pitch accents.
    """

    ip: IntonationalPhrase
    parent: ResynthesizedPhrase

    initial_boundary: InitialBoundary
    words: list[Word]
    final_boundary: FinalBoundary

    _frequency_range: FrequencyRange

    def __init__(self, phrase_ip: IntonationalPhrase, sentence: deque[str], parent: ResynthesizedPhrase):
        """ In this function, we create a ResynthesisedIntonationalPhrase,
         It consists of an initial boundary, all the words with a pitchaccent, and a final boundary """
        
        self.ip = phrase_ip
        self.parent = parent
        
        #Set the initial boundary and do extra processing for unaccented ip's
        str_initial_boundary = sentence.popleft()
        self.fix_unaccented(str_initial_boundary, sentence)
        self.initial_boundary = InitialBoundary(str_initial_boundary, self)
        

        

        #add all words with pitch accent to a list
        self.words: list[Word] = []
        for voiced_portion in phrase_ip.vps:
            str_word = sentence.popleft()
            if str_word:
                word = Word(str_word,
                            self,
                            len(self.words),
                            voiced_portion)
                self.words.append(word)
        
        #Set the final boundary.
        str_final_boundary = sentence.popleft()
        self.final_boundary = FinalBoundary(str_final_boundary, self)

        # We only set this when the decoding starts
        self._frequency_range = None

    def decode(self, point_list):
        # Reset frequency_range
        self.reset_downstep()

        #decode all pitch accents in the ResynthesisedIntonationalPhrase. 
        #decode explained in pitch_accents.py for each class initial_boundary, word and final_boundary
        self.initial_boundary.decode(point_list)
        for word in self.words:
            word.decode(point_list)
        self.final_boundary.decode(point_list)

        self.parent._frequency_range = self.frequency_range

    #these @property defenitions are used to more easily retrieve properties from a previous type within this class.
    @property
    def vars(self) -> ResynthesizedVariables:
        return self.parent.vars

    @property
    def start(self):
        return self.ip.start_time
    @property
    def end(self):
        return self.ip.end_time

    @property
    def frequency_range(self):
        if self._frequency_range:
            return self._frequency_range
        else:
            return self.parent.frequency_range

    #apply the frequency scaling for a downstep.
    def downstep(self, scalar):
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)

    #reset downstep
    def reset_downstep(self):
        self._frequency_range = None
    
    #Check if there is a unaccented ip, if this is the case, we set it as an initial boundary and add an empty word
    #to keep our vp indexing consistent.
    def fix_unaccented(self, str_initial_boundary, sentence):
        """
        Checks if the IP is unaccented. If it is, then we get one pitch
        accent fewer, because the 'L' or 'H' word functions both as an
        initial boundary and as the first word.

        We handle these pitch accents in the initial boundary, but the
        program will get confused by having one fewer pitch accent than
        expected, so we add it back in here.
        """
        if str_initial_boundary in {"H", "L"}:
            sentence.appendleft(None)


@dataclass
class ResynthesizedPhrase:
    """
    The ResynthesizedPhrase is called upon by resynthesis.resynthesize
    to first interpret the pitch accents, and then decode into frequency
    points to be sent to Praat.
    """

    textgrid: tg.TextGrid
    ips:  list[ResynthesizedIntonationalPhrase]
    vars: ResynthesizeVariables

    def __init__(self, phrase: Phrase, sentence: list[str], **kwargs):
        """
        ResynthesizedPhrase takes two main arguments:
          1. phrase: a Phrase, decoded from a TextGrid
          2. sentence: a list of pitch accents, to be used in resynthesis

        Additionally it uses any extra arguments to create the global
        ResynthesizeVariables, which allows for overriding Fr, N, W,
        FROMTIME and so on.
        """

        self.ips: list[ResynthesizedIntonationalPhrase] = []

        # save the textgrid so we can later return a modified one
        self.textgrid = phrase.textgrid

        try:
            #check the gender and set default values accordingly
            gender = self.textgrid[0][0].mark
            match gender:
                case 'm':
                    # here we are careful not to override user-specified
                    # parameters
                    if 'fr' not in kwargs:
                        kwargs['fr'] = 70
                    if 'n' not in kwargs:
                        kwargs['n'] = 70
                    if 'w' not in kwargs:
                        kwargs['w'] = 110
                case 'v':
                    if 'fr' not in kwargs:
                        kwargs['fr'] = 95
                    if 'n' not in kwargs:
                        kwargs['n'] = 120
                    if 'w' not in kwargs:
                        kwargs['w'] = 190
        except Exception:
            # if for some reason there is no first tier in the textgrid,
            # then don't modify the variables
            pass

        # and initialize the global variables
        self.vars = ResynthesizeVariables(**kwargs)

        self.removeP(sentence)

        sentence = deque(sentence)

        

        for phrase_ip in phrase.ips:
            # the resynthesized IP invocation 'eats' the sentence, so
            # that each call removes its own pitch accents from the
            # sentence.
            ip = ResynthesizedIntonationalPhrase(phrase_ip, sentence, self)
            self.ips.append(ip)

        # Set the initial frequency range
        freq_low = self.vars.fr + self.vars.n - 0.5*self.vars.w
        freq_high = self.vars.fr + self.vars.n + 0.5*self.vars.w
        self._frequency_range = FrequencyRange(freq_low, freq_high)


    def removeP(self, sentence):
        for (i, word) in enumerate(sentence):
            if word in ["P"]:
                sentence.pop(i)


    
    def decode(self):
        """
        Decode the whole phrase, returning a list of FrequencyTargets and
        AddTimes. (see `types.py` for their specification)
        """

        # initialise empty list
        point_list = []
        for ip in self.ips:
            # decode each ResynthesizedIntonationalPhrase
            ip.decode(point_list)
        return point_list


    def decode_into_textgrid(self):
        """
        Decode the whole phrase, returning the modified TextGrid with
        two or three added tiers: a frequency tier, containing the new
        pitches for the resynthesized sentence; a target tier,
        containing the labels that belong to these pitches; and, if any
        final lengthening happened, a duration tier to store these.
        """

        # copy so that this method could be called again
        textgrid = copy.deepcopy(self.textgrid)

        # Add pitch accent labels
        word_tier = tg.PointTier('tones', textgrid.minTime, textgrid.maxTime)
        for ip in self.ips:
            word_tier.addPoint(tg.Point(ip.ip.start.total_seconds(), ip.initial_boundary.name))
            for word in ip.words:
                word_tier.addPoint(tg.Point(word.vp.start.total_seconds(), word.name))
            word_tier.addPoint(tg.Point(ip.ip.end.total_seconds(), ip.final_boundary.name))
        textgrid.append(word_tier)

        # Generate the new frequency points
        point_list = self.decode()

        #create tier objects.
        target_tier = tg.PointTier('targets', textgrid.minTime, textgrid.maxTime)
        frequency_tier = tg.PointTier('ToDI-F0', textgrid.minTime, textgrid.maxTime)
        duration_tier = tg.PointTier('duration', textgrid.minTime, textgrid.maxTime)

        #add the newly generated frequency_points to the target_tier and frequency_tier
        for point in point_list:
            # This is a little bit of a hack, because the final
            # lengthening was added later: AddTime points are in the
            # same list as the FrequencyTargets.
            # Here we check which of the two each point is, and add it
            # the TextGrid accordingly.

            if isinstance(point, FrequencyPoint):
                # For each FrequencyPoint, we simply add the label and
                # the pitch:
                target_tier.addPoint(tg.Point(
                    point.time.total_seconds(), point.label))
                frequency_tier.addPoint(tg.Point(
                    point.time.total_seconds(), str(int(point.freq))))

            elif isinstance(point, AddTime):
                # The AddTime needs a little decoding still.

                # Praat uses 'duration' instead of speed, which is its inverse
                speed_inverse = point.new_interval.duration / point.old_interval.duration

                # We add four points: an original speed at the start and
                # end of the intervals, and the new speed just in
                # between that.
                duration_tier.addPoint(tg.Point(
                    point.old_interval.start.total_seconds(),
                    str(speed_inverse)
                ))
                duration_tier.addPoint(tg.Point(
                    point.old_interval.end.total_seconds(),
                    str(speed_inverse)
                ))

                duration_tier.addPoint(tg.Point(
                    (point.old_interval.start - timedelta(microseconds=1)).total_seconds(),
                    '1'
                ))
                duration_tier.addPoint(tg.Point(
                    (point.old_interval.end + timedelta(microseconds=1)).total_seconds(),
                    '1'
                ))

        #add tier to textgrid
        textgrid.append(target_tier)
        textgrid.append(frequency_tier)
        # If any durations were changed, then add the tier:
        if duration_tier:
            textgrid.append(duration_tier)

        return textgrid


    @property
    def frequency_range(self):
        return self._frequency_range

    def downstep(self, scalar):
        """Set the frequency values to the downstepped values."""
        freq_low = self.vars.fr + scalar*(self.frequency_range.low - self.vars.fr)
        freq_high = self.vars.fr + scalar*(self.frequency_range.high - self.vars.fr)
        self._frequency_range = FrequencyRange(freq_low, freq_high)
