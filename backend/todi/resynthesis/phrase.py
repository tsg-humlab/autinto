from dataclasses import dataclass

import textgrid as tg

from resynthesis.types import Seconds, Interval

@dataclass
class VoicedPortion(Interval):
    """
    A VoicedPortion (vp) is an interval with a start_time and an end_time.
    """
    def __init__(self, textgrid_vp):
        start_time = Seconds(textgrid_vp.minTime)
        end_time = Seconds(textgrid_vp.maxTime)
        super().__init__(start_time, end_time)


@dataclass
class IntonationalPhrase(Interval):
    """
    An IntonationalPhrase (ip) is an interval with a start_time and end_time that consists of VoicedPortions (vp's).
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
    A phrase is an interval with a start_time and end_time that is divided in IntentionalPhrases (ip's) and it is also expressed as a textgrid.
    """
    ips: list[IntonationalPhrase]
    textgrid: tg.TextGrid

    def __init__(self, file: str):
		# We expect a textgrid file and we use this to determine the start_time and end_time.
        self.textgrid = tg.TextGrid.fromFile(file) 

        start_time = Seconds(self.textgrid.minTime)
        end_time = Seconds(self.textgrid.maxTime)

        super().__init__(start_time, end_time)
		
		# We also get the ip's and vp's from the textgrid .
        textgrid_ips = self.textgrid.getFirst("IP's")
        textgrid_vps = self.textgrid.getFirst('vp')
		
		# We construct the list of ip's here.
        self.ips: list[IntonationalPhrase] = []
        for textgrid_ip in textgrid_ips:
            if not textgrid_ip.mark:
                continue
            ip = IntonationalPhrase(textgrid_ip, [])
            self.ips.append(ip)
		
		# Here we put the vp's in the ip's.
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
