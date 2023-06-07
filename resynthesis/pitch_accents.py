from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re

from resynthesis.types import Seconds, Milliseconds, FrequencyPoint, Interval, Duration, AddTime
from resynthesis.abstract_pitch_accents import AbstractWord, AbstractInitialBoundary, AbstractFinalBoundary

class Tone(Enum):
    """
    Helper class for the pitch accents. It is simply used to store a
    variable as Tone.HIGH or Tone.LOW (or Tone.HIGH_DOWNSTEPPED)
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
        """
        Decode the primary tone of the word. This is the first tone:
        'L*', 'H*', or '!H*'.
        """

        # We call decode_primary_low() on 'L*'- words,
        # and decode_primary_high() on '(!)H*'- words.
        match self.primary_tone:
            case Tone.LOW:
                self.decode_primary_low(point_list)
            case Tone.HIGH | Tone.HIGH_DOWNSTEPPED as tone:
                # We treat HIGH and HIGH_DOWNSTEPPED identically here.
                # The downstepping logic is then handled in
                # decode_downstep()
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

        decode_downstep() also undoes accentual downsteps in the case of
        a high tone in the final word in the IP.
        """

        match tone:
            case Tone.HIGH_DOWNSTEPPED:
                # This downstep applies to the rest of the phrase if
                # it is not cancelled, but they can still be cancelled
                # in the final word of the IP.
                # If the downstep is not cancelled, it automatically
                # carries over to any later IPs.
                self.ip.downstep(self.vars.accentual_downstep)

            case Tone.HIGH:
                # The cancellation happens right here, if this is the
                # final word of the IP, and the current tone is high.
                if self.is_last_word:
                    # Undo all accentual downsteps
                    self.ip.reset_downstep()

            # Create nice errors for unexpected values:

            # Error for unexpected tone
            case unexpected_tone if isinstance(unexpected_tone, Tone):
                raise ValueError('Expected {} or {}, found {}'.format(
                    Tone.HIGH,
                    Tone.HIGH_DOWNSTEPPED,
                    unexpected_tone))
            # Error for unexpected other value
            case _ as unexpected_value:
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
        if Duration(self.vp.end, self.next_boundary) < Milliseconds(360):
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
        if Duration(self.vp.end, self.next_boundary) < Milliseconds(360):
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
            time_H1 = self.vp.scale(0.4*self.vars.star_time)
            time_H2 = self.vp.scale(0.4*self.vars.star_time + 0.3)
        else:
            time_H1 = self.vp.scale(self.vars.star_time)
            time_H2 = self.vp.scale(2*self.vars.star_time)

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

        if interval.duration < 2 * self.vars.from_time:
            # If there is not enough time, place it 30% into the
            # remaining time.
            time_l = interval.scale(0.30)
        else:
            # Otherwise it's 100 ms after the previous target.
            time_l = last_target_time + self.vars.to_time

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

        # If the final boundary is %, no points are created for this tone,
        # and the method returns early.
        if self.final_boundary == '%':
            return

        # Otherwise, one or two points are created. We make a variable
        # here to determine whether the second point needs to be made:
        make_l2 = False

        time_preceding_target = point_list[-1].time
        spread_space = Interval(time_preceding_target, self.ip.end)
        if spread_space.duration < 2.2 * self.vars.from_time:
            time_l1 = spread_space.scale(0.50)
        else:
            time_l1 = time_preceding_target + self.vars.from_time
            time_l2 = self.ip.end - self.vars.to_time
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

        # This time the frequency of the point is also dependent on the
        # available time.
        vp_end_to_next = Interval(self.vp.end, self.next_boundary)
        if vp_end_to_next.duration < 2*self.vars.to_time:
            time_l1 = vp_end_to_next.scale(0.50)
            freq_l1 = self.scale_frequency(0.40)
        else:
            time_l1 = self.next_boundary - self.vars.to_time
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
        #This case only needs to be handled when it is not the last word in an ip,
        #if it is the last word, we skip this (thanks to the return) and handle this in final boundary handling.
        if self.is_last_word:
            return
        time_preceding_target = point_list[-1].time
        prev_target_to_next = Interval(time_preceding_target, self.next_boundary)
        if prev_target_to_next.duration < 2*self.vars.from_time:
            time_h1 = prev_target_to_next.scale(0.30)
        else:
            time_h1 = self.next_boundary - self.vars.to_time

        point_h1 = FrequencyPoint(
            label = 'h1',
            freq  = self.scale_frequency(0.70),
            time  = time_h1)

        point_list.append(point_h1)


    def from_name(self, name: str):
        """Decode a non-boundary pitch accent string into tones."""

        # Error if we see an unrecognised word:
        if name not in ['H*', '!H*', 'H*L', '!H*L', 'H*LH', 'L*H', 'L*',
                        'L*HL', 'L*!HL']:
            raise ValueError("'{}' is not a valid word.".format(name))

        # Then we extract the tones with a regular expression:
        result = re.findall(r'!?[HL]', name)
        # ^ 'L*!HL' would return ['L', '!H', 'L']

        self.primary_tone = Tone(result[0])
        # If there are more than two tones, then create a middle_tone
        # from the second match:
        self.middle_tone  = Tone(result[1])  if len(result) == 3 else None

        # And if there are two or three tones, create a final_tone from
        # the last match:
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
    # whether the IP is downstepped. A boolean is also creating in the
    # IP that this boundary belongs to, storing whether this is an
    # unaccented IP.
    #
    # See from_name() for the implementation of this decoding.

    first_target_tone: Tone
    second_target_tone: Tone
    has_downstep: bool

    def decode(self, point_list):
        """
        Decode an initial boundary into FrequencyPoints, and append them
        to point_list.
        """

        if self.has_downstep:
            # Phrasal downsteps apply to the entire rest of the phrase,
            # not just the IP itself, so we call self.phrase.downstep()
            self.phrase.downstep(self.vars.phrasal_downstep)

        # Then decode the targets.
        if self.ip.unaccented:
            self.decode_unaccented(point_list)
        else:
            self.decode_first_target(point_list)
            self.decode_second_target(point_list)

    def decode_unaccented(self, point_list):
        """Decode the target for an unaccented IP initial boundary."""

        match self.first_target_tone:
            case Tone.LOW:
                label = 'l1'
                freq = self.scale_frequency(0.15)
            case Tone.HIGH:
                label = 'h1'
                freq = self.scale_frequency(0.6)


    def decode_first_target(self, point_list):
        """Creates a first target for a normal initial boundary."""

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
        Creates a second target for a normal initial boundary, if there
        is enough space before the first word.
        """

        # If the time before the first word is less than `to_time`, then
        # no second target is created, and the function returns early.
        time_to_first_vp = Interval(self.ip.start, self.first_word.vp.start)

        if time_to_first_vp.duration < self.vars.to_time:
            return

        # Otherwise, if there is enough space, but still less than two
        # times `to_time`, the second target is placed halfway between
        # the IP start and the first word.
        elif time_to_first_vp.duration < 2*self.vars.to_time:
            time = time_to_first_vp.scale(0.50)
        # Finally, if there is even more space, then the second target is
        # placed `to_time` before the first word.
        else:
            time = self.first_word.vp.start - self.vars.to_time

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

        # Handle unaccented IPs immediately.
        if name in {'H', 'L'}:
            self.ip.unaccented = True
            self.first_target_tone = Tone(name)
            self.has_downstep = False
        else:
            self.ip.unaccented = False

            if name[0] == '!':
                # We remove the '!' from the word here, and store that
                # the IP is downstepped.
                name = name[1:]
                self.has_downstep = True
            else:
                self.has_downstep = False

            # The first tone is decided by the character directly after the
            # '%' sign, which is always the second character, since we
            # removed the '!' if it existed.
            self.first_target_tone = Tone(name[1])

            # The second target tone is decided by the final character.
            # For words '%L', '%H', '!%H', this means that the first and
            # second tone will be the same!
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
        Handle final lengthening, final word spread, and decode the
        final boundary into frequency points and put them in point_list.
        """

        if not self.ip.unaccented:
            self.decode_final_lengthening(point_list)
            self.decode_nuclear_rise_and_spread(point_list)

        self.decode_final_boundary(point_list)

    def decode_final_lengthening(self, point_list):
        # If there is already time left after the VP, we don't do any
        # final lengthening.
        if self.last_word.vp.end < self.ip.end:
            return

        # Otherwise, the time_to_add still depends on the circumstances.
        if ((self.last_word.name in ['H*L', '!H*L'] and self.name == 'H%')
            or self.last_word == 'L*H'
            or (self.last_word == ['L*HL', 'L*!HL'] and self.name in ['L%', '%'])):

            # Usually only a few ms
            time_to_add = (
                Milliseconds(11.5/self.last_word.vp.duration.total_seconds())
                - Milliseconds(23)
                )

        elif self.last_word.name in ['L*HL', 'L*!HL'] and self.name == 'H%':
            time_to_add = (
                Milliseconds(15.0/self.last_word.vp.duration.total_seconds())
                - Milliseconds(23)
                )

        # And if none of these are the case, then no final lengthening happens.
        else:
            return

        # Also exit if it turns out we're not adding any time!
        if time_to_add <= Milliseconds(0):
            return

        new_ip_end = self.ip.end + time_to_add

        point_list.append(AddTime(
            old_interval=self.last_word.vp,
            new_interval=Interval(self.last_word.vp.start, new_ip_end)
        ))

    def decode_nuclear_rise_and_spread(self, point_list):
        """
        If the last word in the IP was 'L*', 'H*', '!H*', or 'L*H', then
        one or two extra points are created to spread the final tone.
        """

        match self.last_word.name:
            case 'L*':
                # If there is not enough time, don't create extra points
                if Duration(self.last_word.vp.end, self.ip.end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_L4 = FrequencyPoint(
                    label = 'L4',
                    freq = self.scale_frequency(0.2),
                    time = point_list[-1].time + Milliseconds(8))
                point_l2 = FrequencyPoint(
                    label = 'l2',
                    freq = self.scale_frequency(0.2),
                    time = self.ip.end - self.vars.to_time)

                point_list.append(point_L4)
                point_list.append(point_l2)

            case 'H*' | '!H*':
                # If there is not enough time, don't create extra points
                if Duration(self.last_word.vp.end, self.ip.end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_H3 = FrequencyPoint(
                    label = 'H3',
                    freq = self.scale_frequency(0.67),
                    time = point_list[-1].time + Milliseconds(8))
                point_h2 = FrequencyPoint(
                    label = 'h2',
                    freq = self.scale_frequency(0.67),
                    time = self.ip.end - self.vars.to_time)

                point_list.append(point_H3)
                point_list.append(point_h2)

            case 'L*H':
                # With a last word L*H, we create one or two extra
                # points, depending on available time.
                make_h2 = False

                if Duration(point_list[-1].time, self.ip.end) < 2*self.vars.from_time:
                    time_h1 = point_list[-1].time + 0.5*self.vars.to_time
                else:
                    time_h1 = point_list[-1].time + self.vars.from_time
                    time_h2 = self.ip.end - self.vars.to_time
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
