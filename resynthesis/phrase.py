from dataclasses import dataclass
import textgrid as tg

from resynthesis.types import Milliseconds, Interval

@dataclass
class VoicedPortion(Interval):
    def __init__(self, start_time, end_time):
        super().__init__(start_time, end_time)


@dataclass
class IntonationalPhrase(Interval):
    vps: list[VoicedPortion]

    def __init__(self, start_time, end_time, vps):
        super().__init__(start_time, end_time)
        self.vps = vps


@dataclass
class Phrase(Interval):
    textgrid: tg.TextGrid
    ips: list[IntonationalPhrase]

    def __init__(self, file: str):
        self.textgrid = tg.TextGrid.fromFile(file) 
        super().__init__(self.textgrid.minTime, self.textgrid.maxTime)

        textgrid_ips = self.textgrid.getFirst("IP's")
        textgrid_vps = self.textgrid.getFirst('vp')

        self.ips: list[IntonationalPhrase] = []
        for textgrid_ip in textgrid_ips:
            if not textgrid_ip.mark:
                continue
            ip = IntonationalPhrase(textgrid_ip.minTime, textgrid_ip.maxTime, [])
            self.ips.append(ip)

        for textgrid_vp in textgrid_vps:
            if not textgrid_vp.mark:
                continue

            vp = VoicedPortion(textgrid_vp.minTime, textgrid_vp.maxTime)
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
