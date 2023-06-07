"""
resynthesis.phrase

Handles the decoding of TextGrid files into a Phrase, which consists of
one or more IntonationalPhrases, which in turn consist of VoicedPortions.
"""

from dataclasses import dataclass

import textgrid as tg

from resynthesis.types import Seconds, Interval

@dataclass
class VoicedPortion(Interval):
    """
    A VoicedPortion (vp) is an interval with a start_time and an
    end_time, and is linked to a Word during decoding/resynthesizing.
    """
    def __init__(self, textgrid_vp):
                     # textgrid times are in seconds
        start_time = Seconds(textgrid_vp.minTime)
        end_time = Seconds(textgrid_vp.maxTime)
        super().__init__(start_time, end_time)


@dataclass
class IntonationalPhrase(Interval):
    """
    An IntonationalPhrase (ip) is an interval with a start_time and
    end_time, that also contains a list of VoicedPortions (vp's).
    """
    vps: list[VoicedPortion]

    def __init__(self, textgrid_ip, vps):
        start_time = Seconds(textgrid_ip.minTime)
        end_time = Seconds(textgrid_ip.maxTime)

        super().__init__(start_time, end_time)
        self.vps = vps


@dataclass
class Phrase(Interval):
    """
    A Phrase is, again, an interval with a start_time and end_time. It
    contains a list of IntonationalPhrases, and also maintains a handle
    to the TextGrid it was created with.
    """

    ips: list[IntonationalPhrase]
    textgrid: tg.TextGrid

    def __init__(self, filename: str):
        # We expect a TextGrid file and we use this to determine the
        # start_time and end_time.
        self.textgrid = tg.TextGrid.fromFile(filename) 

        start_time = Seconds(self.textgrid.minTime)
        end_time = Seconds(self.textgrid.maxTime)

        super().__init__(start_time, end_time)

        # We also get the IP and VP tiers from the textgrid .
        textgrid_ips = self.textgrid.getFirst("IP's")
        textgrid_vps = self.textgrid.getFirst('vp')

        # Then construct each IP and add them to the list.
        self.ips: list[IntonationalPhrase] = []
        for textgrid_ip in textgrid_ips:
            if not textgrid_ip.mark:
                continue
            ip = IntonationalPhrase(textgrid_ip, [])
            self.ips.append(ip)

        # Lastly, insert the VPs into the IPs
        for textgrid_vp in textgrid_vps:
            if not textgrid_vp.mark:
                continue

            vp = VoicedPortion(textgrid_vp)
            # Put this VP in the IP that its start_time falls in.
            done = False
            for ip in self.ips:
                if vp.start_time >= ip.start_time and vp.start_time <= ip.end_time:
                    ip.vps.append(vp)
                    done = True
                    break

            # If the start_time was not in any IP, then put this VP in
            # the IP that its end_time falls in.
            if done:
                continue
            for ip in self.ips:
                if vp.end_time >= ip.start_time and vp.end_time <= ip.end_time:
                    ip.vps.append(vp)
                    done = True
                    break

            # Otherwise, the VP belongs in no IP, and that's an error.
            assert done, 'VP was not found to belong in any IP'
