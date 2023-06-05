from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re

from resynthesis.types import Milliseconds, FrequencyPoint, Interval
from resynthesis.abstract_pitch_accents import AbstractWord, AbstractInitialBoundary, AbstractFinalBoundary

def duration(start, end):
    """
    Slightly shorter syntax for creating an interval, then asking for
    its duration.
    """
    return Interval(start, end).duration

class Tone(Enum):
    """
    Helper class for the pitch accents. It is simply used to store a
    variable as Tone.HIGH or Tone.LOW
    """

    LOW  = 'L'
    HIGH = 'H'
    HIGH_DOWNSTEPPED = '!H'


class Word(AbstractWord):
    """
    This class interprets words, or all pitch accents that are not
    initial or final boundaries. It implements the two required methods:
    decode() and from_name().

    (For more information on implementing your own Word class, or for
     under-the-hood details, take a look at abstract_pitch_accents.py in
     this same folder.)
    """

    # A word consists of up to three tones.
    # All words start with L*, H*, or !H*; this is the primary tone.
    primary_tone: Tone
    # Middle tones are only present in words with three tones, like L*HL
    # and H*LH.
    middle_tone:  Optional[Tone] = None
    # The final tone is present in all words with at least two tones.
    final_tone:   Optional[Tone] = None

    def decode(self, point_list):
        """
        Decode an word into FrequencyPoints, and append them to
        point_list.
        """

        self.decode_primary(point_list)
        self.decode_middle(point_list)
        self.decode_final(point_list)


    def decode_primary(self, point_list):
        # We call decode_primary_low() on 'L*'- words,
        # and decode_primary_high() on '(!)H*'- words.
        match self.primary_tone:
            case Tone.LOW:
                self.decode_primary_low(point_list)
            case Tone.HIGH | Tone.HIGH_DOWNSTEPPED as tone:
                self.decode_downstep(tone)
                self.decode_primary_high(point_list)

    def decode_middle(self, point_list):
        # Same as decode_primary, but because the middle tone is
        # optional, we add a (technically redundant) case for handling
        # a lack of a middle tone, in which case we do nothing.
        match self.middle_tone:
            case Tone.LOW:
                self.decode_middle_low(point_list)
            case Tone.HIGH | Tone.HIGH_DOWNSTEPPED as tone:
                self.decode_downstep(tone)
                self.decode_middle_high(point_list)
            case None:
                pass

    def decode_final(self, point_list):
        match self.final_tone:
            case Tone.LOW:
                self.decode_final_low(point_list)
            case Tone.HIGH | Tone.HIGH_DOWNSTEPPED as tone:
                self.decode_downstep(tone)
                self.decode_final_high(point_list)
            case None:
                return


    def decode_downstep(self, tone: Tone):
        """
        ACCENTUAL DOWNSTEP
        The rule lowers the upper and lower boundaries of the pitch
        range.

        This method also undoes accentual downsteps in the case of a
        high tone in the final word in the IP.
        """

        match tone:
            case Tone.HIGH_DOWNSTEPPED:
                # This downstep applies to the rest of the phrase if
                # they are not cancelled, but they can still be
                # cancelled in the final word of the IP. For now, the
                # downstep is applied only to the IP, and in the
                # FinalBoundary handling, any remaining downsteps are
                # applied to the phrase.
                print('downstepping')
                self.ip.downstep(0.7)

            case Tone.HIGH:
                # The cancellation happens right here, if this is the
                # final word of the IP, and the current tone is high.
                if self.is_last_word:
                    # Undo all accentual downsteps
                    self.ip.reset_downstep()

            # Create nice errors for unexpected values:
            case unexpected_tone if isinstance(unexpected_tone, Tone):
                # Error for unexpected tone
                raise ValueError('Expected {} or {}, found {}'.format(
                    Tone.HIGH,
                    Tone.HIGH_DOWNSTEPPED,
                    unexpected_tone))
            case _ as unexpected_value:
                # Error for unexpected different value
                raise TypeError('Expected {}, found {}'.format(
                    Tone,
                    type(unexpected_value)))


    def decode_primary_low(self, point_list):
        """
        LOW TRAY FOR L*
        This rule creates an extended dip for L*.
        """

        # Point L1 always comes just before the VP. Points L2 and L3 are
        # placed depending on the amount of time available *after* the
        # current VP.

        # If there is a boundary (either the IP ends or the next VP
        # starts) within 360 milliseconds, L2 and L3 are placed
        # according to the available space from the VP start to the
        # boundary.
        if duration(self.vp.end, self.next_boundary) < Milliseconds(360):
            # define a new interval from VP start to next boundary
            start_to_next_boundary = Interval(self.vp.start, self.next_boundary)
            # then place points 3% and 30% into this interval
            time_L2 = start_to_next_boundary.scale(0.03)
            time_L3 = start_to_next_boundary.scale(0.30)
        # Otherwise, if there is enough time after the VP:
        else:
            # L2 and L3 are placed depending only on the VP itself.
            time_L2 = self.vp.scale(0.05)
            time_L3 = self.vp.scale(0.75)


        # Then the frequency points are created.
        point_L1 = FrequencyPoint(
            label = 'L1',
            freq  = self.scale_frequency(0.2),
            time  = self.vp.start - Milliseconds(10))
        point_L2 = FrequencyPoint(
            label = 'L2',
            freq  = self.scale_frequency(0.15),
            time  = time_L2)
        point_L3 = FrequencyPoint(
            label = 'L3',
            freq  = self.scale_frequency(0.15),
            time  = time_L3)

        point_list.append(point_L1)
        point_list.append(point_L2)
        point_list.append(point_L3)


    def decode_middle_high(self, point_list):
        """
        DELAYED PEAK
        This rule creates a delayed peak after L*.
        """

        # TODO downstep

        # Cases are split the same way they were in decode_primary_low().
        if duration(self.vp.end, self.next_boundary) < Milliseconds(360):
            # If time is short it is again dependent on the interval
            # from VP start to the next boundary.
            start_to_next_boundary = Interval(self.vp.start, self.next_boundary)
            time_H1 = start_to_next_boundary.scale(0.60)
            time_H2 = start_to_next_boundary.scale(0.70)

        else:
            # Here we use the preceding point's time to place H1 and H2.
            last_point_time = point_list[-1].time

            time_H1 = last_point_time + 0.5 * (self.vp.duration + Milliseconds(360))
            time_H2 = last_point_time + 0.7 * (self.vp.duration + Milliseconds(360))


        point_H1 = FrequencyPoint(
            label = 'H1',
            freq  = self.scale_frequency(0.70),
            time  = time_H1)
        point_H2 = FrequencyPoint(
            label = 'H2',
            freq  = self.scale_frequency(0.70),
            time  = time_H2)

        point_list.append(point_H1)
        point_list.append(point_H2)



    def decode_primary_high(self, point_list):
        """
        FLAT-TOP PEAK
        This rule creates the first and second targets of H* in its VP.
        """

        if self.vp.duration < Milliseconds(250):
            # The points are placed a little earlier if the VP is short.
            time_H1 = self.vp.scale(0.12)
            time_H2 = self.vp.scale(0.42)
        else:
            time_H1 = self.vp.scale(0.30)
            time_H2 = self.vp.scale(0.60)

        point_H1 = FrequencyPoint(
            label = 'H1',
            freq  = self.scale_frequency(0.7),
            time  = time_H1)
        point_H2 = FrequencyPoint(
            label = 'H2',
            freq  = self.scale_frequency(0.7),
            time  = time_H2)

        point_list.append(point_H1)
        point_list.append(point_H2)


    def decode_middle_low(self, point_list):
        """
        PRENUCLEAR RISE
        This rule creates  the fall from H* in H*LH.
        """

        # Note that this method will not be called in the word H*L,
        # because there L is the final tone, so it will call
        # decode_final_low() instead.

        last_target_time = point_list[-1].time

        # The timing of this point is, again, dependent on the available
        # window. Here it depends on the window between the preceding
        # target and the next boundary (IP end or next VP start).
        interval = Interval(last_target_time, self.next_boundary)

        if interval.duration < Milliseconds(200):
            # If there is not enough time, place it 30% into the
            # remaining time.
            time_l = interval.scale(0.30)
        else:
            # Otherwise it's 100 ms after the previous target.
            time_l = last_target_time + Milliseconds(100)

        point_l = FrequencyPoint(
            label = '+l',
            freq  = self.scale_frequency(0.4),
            time  = time_l)

        point_list.append(point_l)


    def decode_final_low(self, point_list):
        """
        Decodes a final low tone. Applicable to words 'H*L', '!H*L',
        'L*HL', and 'L*!HL'.

        Timing depends on whether another word follows in this IP or
        not.
        """

        if self.is_last_word:
            self.decode_nuclear_fall(point_list)
        else:
            self.decode_pre_nuclear_fall(point_list)

    def decode_nuclear_fall(self, point_list):
        """
        NUCLEAR FALL
        This rule creates a fast nuclear fall after (!)H*L and L*(!)HL.

        Only executed if this is the final word in the IP.
        """

        # If the final boundary is %, no points are created, and the
        # method returns early.
        if self.final_boundary == '%':
            return

        # Otherwise, one or two points are created. We make a variable
        # here to determine whether the second point needs to be made:
        make_l2 = False

        time_preceding_target = point_list[-1].time
        spread_space = Interval(time_preceding_target, self.ip.end)
        if spread_space.duration < Milliseconds(220):
            time_l1 = spread_space.scale(0.50)
        else:
            time_l1 = time_preceding_target + Milliseconds(100)
            time_l2 = self.ip.end - Milliseconds(100)
            make_l2 = True

        point_l1 = FrequencyPoint(
            label = 'l1',
            freq = self.scale_frequency(0.15),
            time = time_l1)
        point_list.append(point_l1)

        if make_l2:
            point_l2 = FrequencyPoint(
                label = 'l2',
                freq = self.scale_frequency(0.15),
                time = time_l2)
            point_list.append(point_l2)

    def decode_pre_nuclear_fall(self, point_list):
        """
        PRE-NUCLEAR FALL
        This rule creates a slow fall before another toneword.
        """

        # This time both the timing and the frequency of the point are
        # dependent on the available time.
        vp_end_to_next = Interval(self.vp.end, self.next_boundary)
        if vp_end_to_next.duration < Milliseconds(200):
            time_l1 = vp_end_to_next.scale(0.50)
            freq_l1 = self.scale_frequency(0.40)
        else:
            time_l1 = self.next_boundary - Milliseconds(100)
            freq_l1 = self.scale_frequency(0.25)

        point_l1 = FrequencyPoint(
            label = 'l1',
            freq = freq_l1,
            time = time_l1)

        point_list.append(point_l1)


    def decode_final_high(self, point_list):
        """
        PRE-NUCLEAR FALLRISE
        This rule creates the rise from L and L* to the next primary
        tone.
        """

        time_preceding_target = point_list[-1].time
        prev_target_to_next = Interval(time_preceding_target, self.next_boundary)
        if prev_target_to_next.duration < Milliseconds(200):
            time_h1 = prev_target_to_next.scale(0.30)
        else:
            time_h1 = self.next_boundary - Milliseconds(100)

        point_h1 = FrequencyPoint(
            label = 'h1',
            freq  = self.scale_frequency(0.70),
            time  = time_h1)

        point_list.append(point_h1)


    def from_name(self, name: str):
        # Error if we see an unrecognised word
        if name not in ['H*', '!H*', 'H*L', '!H*L', 'H*LH', 'L*H', 'L*',
                        'L*HL', 'L*!HL']:
            raise ValueError("'{}' is not a valid word.".format(name))

        result = re.findall(r'!?[HL]', name)
        # ^ 'L*!HL returns ['L', '!H', 'L']

        self.primary_tone = Tone(result[0])
        self.middle_tone  = Tone(result[1])  if len(result) > 2 else None
        self.final_tone   = Tone(result[-1]) if len(result) > 1 else None


class InitialBoundary(AbstractInitialBoundary):
    """
    This class handles the decoding of an Initial Boundary into
    frequency targets.

    It implements the two methods required from it by the rest of the
    program: decode() and from_name().
    """

    # The word is decoded into a first target tone and a second target
    # tone, each of which can be LOW or HIGH, and a boolean storing
    # whether the IP is downstepped.
    #
    # See from_name() for the implementation of this decoding.
    first_target_tone: Tone
    second_target_tone: Tone
    has_downstep: bool
    is_unaccented: bool

    def decode(self, point_list):
        """
        Decode an initial boundary into FrequencyPoints, and append them
        to point_list.
        """

        if self.has_downstep:
            # Phrasal downsteps apply to the entire rest of the phrase,
            # not just the IP itself
            self.phrase.downstep(0.9)

        # Then decode the targets.
        self.decode_first_target(point_list)
        if not self.is_unaccented:
            self.decode_second_target(point_list)

    def decode_first_target(self, point_list):
        """Creates a first target."""

        if self.is_unaccented:
            match self.first_target_tone:
                case Tone.LOW:
                    label = 'l1'
                    freq = self.scale_frequency(0.15)
                case Tone.HIGH:
                    label = 'h1'
                    freq = self.scale_frequency(0.6)
        else:
            match self.first_target_tone:
                case Tone.LOW:
                    label = 'LB1'
                    freq = self.scale_frequency(0.30)
                case Tone.HIGH:
                    label = 'HB1'
                    freq = self.scale_frequency(0.85)

        first_target = FrequencyPoint(
            label = label,
            freq  = freq,
            # The first target always appears on the IP start.
            time  = self.ip.start)

        point_list.append(first_target)

    def decode_second_target(self, point_list):
        """
        Creates a second target, if there is enough space before the
        first word.
        """

        # If there are less than 100 milliseconds before the first word,
        # then no second target is created, and the function returns
        # early.
        time_to_first_vp = Interval(self.ip.start, self.first_word.vp.start)

        if time_to_first_vp.duration < Milliseconds(100):
            return

        # Otherwise, if there are less than 200 milliseconds, the second
        # target is placed halfway between the IP start and the first
        # word.
        elif time_to_first_vp.duration < Milliseconds(200):
            time = time_to_first_vp.scale(0.50)
        # Finally, if there *are* at least 200 milliseconds, then the
        # second target is placed 100 milliseconds before the first
        # word.
        else:
            time = self.first_word.vp.start - Milliseconds(100)

        # Next, the label and frequency are dependent on the tone.
        match self.second_target_tone:
            case Tone.LOW:
                label = 'LB2'
                freq = self.scale_frequency(0.20)
            case Tone.HIGH:
                label = 'HB2'
                freq = self.scale_frequency(0.70)

        second_target = FrequencyPoint(
            label = label,
            freq = freq,
            time = time)

        point_list.append(second_target)


    def from_name(self, name: str):
        """
        Decodes an initial boundary string into class variables
        first_target_tone, second_target_tone, and has_downstep.
        """

        # Create a nice error for unrecognised words.
        if name not in ['%L', '%H', '%HL', '!%L', '!%H', '!%HL', 'H', 'L']:
            raise ValueError("'{}' is not a valid initial boundary.".format(name))

        if name[0] == '!':
            # We remove the '!' from the word here.
            name = name[1:]
            self.has_downstep = True
        else:
            self.has_downstep = False

        if name in {'H', 'L'}:
            self.is_unaccented = True
            self.first_target_tone = Tone(name)
        else:
            self.is_unaccented = False


            # The first tone is decided by the character directly after the
            # '%' sign, which is always the second character, since we
            # removed the '!' if it existed.
            self.first_target_tone = Tone(name[1])

            # The second target tone is decided by the final character.
            # For words '%L', '%H', '!%H', this means that the first and
            # second tone will be the same.
            self.second_target_tone = Tone(name[-1])


class FinalBoundary(AbstractFinalBoundary):
    """
    This class handles the decoding of a Final Boundary into frequency
    targets.

    It implements the two methods required from it by the rest of the
    program: decode() and from_name().
    """

    def decode(self, point_list):
        """
        Decode the final boundary into frequency points and put them in
        point_list.
        """
        if not self.ip.initial_boundary.is_unaccented:
            self.decode_nuclear_rise_and_spread(point_list)
        self.decode_final_boundary(point_list)

    def decode_nuclear_rise_and_spread(self, point_list):
        """
        If the last word in the IP was 'L*', 'H*', '!H*', or 'L*H', then
        one or two extra points are created to spread the final tone.
        """

        match self.last_word.name:
            case 'L*':
                # If there is not enough time, don't create extra points
                if duration(self.last_word.vp.end, self.ip.end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_L4 = FrequencyPoint(
                    label = 'L4',
                    freq = self.scale_frequency(0.2),
                    time = point_list[-1].time + Milliseconds(8))
                point_l2 = FrequencyPoint(
                    label = 'l2',
                    freq = self.scale_frequency(0.2),
                    time = self.ip.end - Milliseconds(100))

                point_list.append(point_L4)
                point_list.append(point_l2)

            case 'H*' | '!H*':
                # If there is not enough time, don't create extra points
                if duration(self.last_word.vp.end, self.ip.end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_H3 = FrequencyPoint(
                    label = 'H3',
                    freq = self.scale_frequency(0.67),
                    time = point_list[-1].time + Milliseconds(8))
                point_h2 = FrequencyPoint(
                    label = 'h2',
                    freq = self.scale_frequency(0.67),
                    time = self.ip.end - Milliseconds(100))

                point_list.append(point_H3)
                point_list.append(point_h2)

            case 'L*H':
                # With a last word L*H, we create one or two extra
                # points, depending on available time.
                make_h2 = False

                if duration(point_list[-1].time, self.ip.end) < Milliseconds(200):
                    time_h1 = point_list[-1].time + Milliseconds(50)
                else:
                    time_h1 = point_list[-1].time + Milliseconds(100)
                    time_h2 = self.ip.end - Milliseconds(100)
                    if time_h1 != time_h2:
                        # Praat does not like multiple points on the same
                        # millisecond, and as these are the same frequency
                        # anyway, we can simply drop the second if it would
                        # otherwise cause conflicts.
                        make_h2 = True

                point_h1 = FrequencyPoint(
                    label = 'h1',
                    freq = self.scale_frequency(0.60),
                    time = time_h1)
                point_list.append(point_h1)

                if make_h2:
                    point_h2 = FrequencyPoint(
                        label = 'h2',
                        freq = self.scale_frequency(0.60),
                        time = time_h2)
                    point_list.append(point_h2)

            # For any other words, no final lengthening happens.
            case _:
                pass


    def decode_final_boundary(self, point_list):
        """Creates the final target at the IP end border."""

        match self.name:
            case 'L%':
                label = 'LE'
                freq = self.scale_frequency(0.0)
            case 'H%':
                label = 'HE'
                freq = self.scale_frequency(1.0) # TODO handle downstep
            case '%':
                label = 'ME'
                if not self.ip.words:
                    freq = self.scale_frequency(0.40)
                else:
                    match self.last_word.name:
                        case 'H*L' | '!H*L' | 'L*HL' | 'L*!HL':
                            freq = self.scale_frequency(0.40)
                        case 'H*' | '!H*' | 'L*H':
                            freq = self.scale_frequency(0.60)
                        case 'L*':
                            freq = self.scale_frequency(0.20)
                        case _:
                            # This case should not happen. For stability
                            # we will simply not create an ME point, instead
                            # of raising an error.
                            return

        point = FrequencyPoint(
            label = label,
            freq = freq,
            time = self.ip.end)

        point_list.append(point)


    def from_name(self, name: str):
        # The final boundary is so simple that we can simply use
        # self.name in the main logic (which is always available).

        # We do still check for illegal words:
        if name not in ['L%', 'H%', '%']:
            raise ValueError("'{}' is not a valid final boundary.".format(name))
        pass
