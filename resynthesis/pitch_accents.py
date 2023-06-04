from dataclasses import dataclass
from enum import Enum
from typing import Optional
import re

from resynthesis.types import Milliseconds, FrequencyPoint
from resynthesis.abstract_pitch_accents import AbstractWord, AbstractInitialBoundary, AbstractFinalBoundary

class Tone(Enum):
    HIGH = 1
    LOW  = 2

    @staticmethod
    def from_name(name: str):
        match name:
            case 'L':
                return Tone.LOW
            case 'H':
                return Tone.HIGH
            case '!H':
                # TODO Downstep
                return Tone.HIGH


class Word(AbstractWord):
    primary_tone: Tone
    middle_tone:  Optional[Tone] = None
    final_tone:   Optional[Tone] = None

    def decode(self, point_list):
        self.decode_primary(point_list)
        self.decode_middle(point_list)
        self.decode_final(point_list)


    def decode_primary(self, point_list):
        match self.primary_tone:
            case Tone.LOW:
                self.decode_primary_low(point_list)
            case Tone.HIGH:
                self.decode_primary_high(point_list)

    def decode_middle(self, point_list):
        match self.middle_tone:
            case None:
                return
            case Tone.HIGH:
                self.decode_middle_high(point_list)
            case Tone.LOW:
                self.decode_middle_low(point_list)

    def decode_final(self, point_list):
        match self.final_tone:
            case None:
                return
            case Tone.LOW:
                self.decode_final_low(point_list)
            case Tone.HIGH:
                self.decode_final_high(point_list)
    

    def decode_primary_low(self, point_list):
        # LOW TRAY FOR L*, PLUS DELAYED PEAK
        # This rule creates an extended dip for L*.

        # Point L1 always comes just before the VP. Points L2 and L3 are
        # placed depending on the amount of time available after the
        # current VP.

        # If there is enough time, L2 and L3 are placed in the VP
        # directly:
        if self.time_to_next_boundary > Milliseconds(360):
            time_L2 = self.vp_start + 0.05 * self.vp_duration
            time_L3 = self.vp_start + 0.75 * self.vp_duration
        # Otherwise, if there is a boundary (either the IP ends or the
        # next VP starts) within 360 milliseconds, the available space
        # is calculated, and L2 and L3 are placed depending on that:
        else:
            time_L2 = self.vp_start + 0.03 * self.delayspace
            time_L3 = self.vp_start + 0.30 * self.delayspace

        # TODO comment here
        point_L1 = FrequencyPoint(
            label = 'L1',
            freq  = self.scale_frequency(0.2),
            time  = self.vp_start - Milliseconds(10))
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
        #LOW TRAY FOR L*, PLUS DELAYED PEAK
        # This rule creates a delayed peak after L*

        # TODO downstep

        if self.time_to_next_boundary > Milliseconds(360):
            # Since there is enough space, the last point, L3, has been
            # placed at 0.75 into the VP.
            last_point_time = self.vp_start + 0.75*self.vp_duration

            time_H1 = last_point_time + 0.5 * self.delayspace
            time_H2 = last_point_time + 0.7 * self.delayspace
        else:
            time_H1 = self.vp_start + 0.60 * self.delayspace
            time_H2 = self.vp_start + 0.70 * self.delayspace



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
        # FLAT-TOP PEAK
        # This rule creates the first and second targets of H* in its
        # VP.

        if self.vp_duration < Milliseconds(250):
            time_H1 = self.vp_start + 0.12 * self.vp_duration
            time_H2 = self.vp_start + 0.42 * self.vp_duration
        else:
            time_H1 = self.vp_start + 0.30 * self.vp_duration
            time_H2 = self.vp_start + 0.60 * self.vp_duration

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
        # PRENUCLEAR RISE AND FALL-RISE
        # This rule creates  the fall from H* in H*LH.

        last_target_time = point_list[-1].time
        if self.next_boundary - last_target_time < Milliseconds(200):
            time_l = last_target_time + 0.30 * (self.next_vp_start - last_target_time)
        else:
            time_l = last_target_time + Milliseconds(100)


        point_l = FrequencyPoint(
            label = '+l',
            freq  = self.scale_frequency(0.4),
            time  = time_l)
        
        point_list.append(point_l)


    def decode_final_low(self, point_list):
        if not self.is_last_word:
            self.decode_pre_nuclear_fall(point_list)
        else:
            self.decode_nuclear_fall(point_list)

    def decode_pre_nuclear_fall(self, point_list):
        # PRE-NUCLEAR FALL
        # This rule creates a slow fall before another toneword.

        if self.time_to_next_boundary < Milliseconds(200):
            time_l1 = self.vp_end + 0.5*self.time_to_next_word
            freq_l1 = self.scale_frequency(0.40)
        else:
            time_l1 = self.vp_end + self.time_to_next_boundary - Milliseconds(100)
            freq_l1 = self.scale_frequency(0.25)

        point_l1 = FrequencyPoint(
            label = 'l1',
            freq = freq_l1,
            time = time_l1)

        point_list.append(point_l1)

    def decode_nuclear_fall(self, point_list):
        # NUCLEAR FALL
        # This rule creates a fast nuclear fall after (!)H*L and
        # (!)L*HL.

        # If the final boundary is %, no points are created, and the
        # method returns early.
        if self.final_boundary == '%':
            return

        # Otherwise, one or two points are created. We make a variable
        # here to store whether the second point needs to be made:
        make_l2 = False

        time_preceding_target = point_list[-1].time
        spread_space = self.ip_end - time_preceding_target
        if spread_space < Milliseconds(220):
            time_l1 = time_preceding_target + 0.5*spread_space
        else:
            time_l1 = time_preceding_target + Milliseconds(100)
            time_l2 = self.ip_end - Milliseconds(100)
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


    def decode_final_high(self, point_list):
        time_preceding_target = point_list[-1].time
        if self.next_boundary - time_preceding_target < Milliseconds(200):
            time_h1 = time_preceding_target + 0.30 * (self.next_boundary - time_preceding_target)
        else:
            time_h1 = self.next_boundary - Milliseconds(100)

        point_h1 = FrequencyPoint(
            label = 'h1',
            freq  = self.scale_frequency(0.70),
            time  = time_h1)

        point_list.append(point_h1)


    def from_name(self, name: str):
       result = re.findall(r'!?[HL]\*?', name)
       # ^ 'L*!HL returns ['L*', '!H', 'L']

       self.primary_tone = Tone.from_name(result[0][:-1])
       self.final_tone   = Tone.from_name(result[-1]) if len(result) > 1 else None
       self.middle_tone  = Tone.from_name(result[1])  if len(result) > 2 else None


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

    def decode(self, point_list):
        """
        Decode an initial boundary into FrequencyPoints, and append them
        to point_list.
        """

        if self.has_downstep:
            # Phrasal downsteps apply to the whole rest of the phrase,
            # not just the IP itself
            self.phrase.downstep(0.9)

        # Then decode the targets.
        self.decode_first_target(point_list)
        self.decode_second_target(point_list)

    def decode_first_target(self, point_list):
        """Creates a first target."""

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
            time  = self.ip_start)

        point_list.append(first_target)

    def decode_second_target(self, point_list):
        """
        Creates a second target, if there is enough space before the
        first word.
        """

        # If there are less than 100 milliseconds before the first word,
        # then no second target is created, and the function returns
        # early.
        if self.time_to_first_word < Milliseconds(100):
            return

        # Otherwise, if there are less than 200 milliseconds, the second
        # target is placed halfway between the IP start and the first
        # word.
        elif self.time_to_first_word < Milliseconds(200):
            time = self.ip_start + 0.5*self.time_to_first_word
        # Finally, if there *are* at least 200 milliseconds, then the
        # second target is placed 100 milliseconds before the first
        # word.
        else:
            time = self.first_word.vp_start - Milliseconds(100)

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
        if name not in ['%L', '%H', '%HL', '!%L', '!%H', '!%HL']:
            raise ValueError("Expected initial boundary, found '{}'".format(name))

        if name[0] == '!':
            # We remove the '!' from the word here.
            name = name[1:]
            self.has_downstep = True
        else:
            self.has_downstep = False

        # The first tone is decided by the character directly after the
        # '%' sign, which is always the second character, since we
        # removed the '!' if it existed.
        self.first_target_tone = Tone.from_name(name[1])

        # The second target tone is decided by the final character.
        # For words '%L', '%H', '!%H', this means that the first and
        # second tone will be the same.
        self.second_target_tone = Tone.from_name(name[-1])


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
                if (self.ip_end - self.last_word.vp_end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_L4 = FrequencyPoint(
                    label = 'L4',
                    freq = self.scale_frequency(0.2),
                    time = point_list[-1].time + Milliseconds(8))
                point_l2 = FrequencyPoint(
                    label = 'l2',
                    freq = self.scale_frequency(0.2),
                    time = self.ip_end - Milliseconds(100))

                point_list.append(point_L4)
                point_list.append(point_l2)

            case 'H*' | '!H*':
                # If there is not enough time, don't create extra points
                if (self.ip_end - self.last_word.vp_end) < Milliseconds(350):
                    return

                # Otherwise, create two points:
                point_H3 = FrequencyPoint(
                    label = 'H3',
                    freq = self.scale_frequency(0.67),
                    time = point_list[-1].time + Milliseconds(8))
                point_h2 = FrequencyPoint(
                    label = 'h2',
                    freq = self.scale_frequency(0.67),
                    time = self.ip_end - Milliseconds(100))

                point_list.append(point_H3)
                point_list.append(point_h2)

            case 'L*H':
                # With a last word L*H, we create one or two extra
                # points, depending on available time.
                make_h2 = False

                if (self.ip_end - point_list[-1].time) < Milliseconds(200):
                    time_h1 = point_list[-1].time + Milliseconds(50)
                else:
                    time_h1 = point_list[-1].time + Milliseconds(100)
                    time_h2 = self.ip_end - Milliseconds(100)
                    if (time_h2 - time_h1) >= Milliseconds(1):
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
                match self.last_word.name:
                    case 'H*L' | '!H*L' | 'L*HL' | 'L*!HL':
                        freq = self.scale_frequency(0.40)
                    case 'H*' | '!H*' | 'L*H':
                        freq = self.scale_frequency(0.60)
                    case 'L*':
                        freq = self.scale_frequency(0.20)
                    case _:
                        # This case should not happen. For stability
                        # we will simply not create an ME point instead
                        # of raising an error.
                        return

        point = FrequencyPoint(
            label = label,
            freq = freq,
            time = self.ip_end)

        point_list.append(point)


    def from_name(self, name: str):
        # The final boundary is so simple that we can simply use
        # self.name in the main logic (which is always available).

        # We do still check for illegal words:
        if name not in ['L%', 'H%', '%']:
            raise ValueError("Expected final boundary, found '{}'".format(name))
        pass
