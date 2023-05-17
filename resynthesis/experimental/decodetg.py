import tgt
from priv_types import Phrase, IntonationalPhrase
from oop_resynth import InitialBoundary

def intervals_from_textgrid(tg_filename: str) -> Phrase:
    textgrid = tgt.read_textgrid(tg_filename)
    intonational_phrase_intervals = textgrid.get_tier_by_name("IP's").intervals
    voiced_portion_intervals = textgrid.get_tier_by_name("vp").intervals

    print(len(voiced_portion_intervals), " voiced portion intervals found")

    phrase = Phrase(ips=[])
    for ip in intonational_phrase_intervals:
        words_in_ip = []
        while (len(voiced_portion_intervals) > 0
                and voiced_portion_intervals[0].start_time >= ip.start_time
                and voiced_portion_intervals[0].end_time <= ip.end_time):
            words_in_ip.append(voiced_portion_intervals.pop(0))
        phrase.ips.append(IntonationalPhrase(phrase, ip, words_in_ip))

    return phrase

def do_the_stuff(accents: list[str], phrase: Phrase):
    print(len(phrase.ips[0].voiced_portions), " voiced portions found.")
    print(len(accents), " accents found.")
    resynth_points = []
    accents.reverse() # to efficiently remove items from what was the start
    for ip in phrase.ips:
        initial_boundary = InitialBoundary(accents.pop(), ip)
        resynth_points.extend(
            initial_boundary.decode()
        )

        for vp in ip.voiced_portions:
            # TODO add handling of regular accents (not initial and final boundary
            accents.pop()

        accents.pop()
        # final_boundary = FinalBoundary(accents.pop(), ip)
        # resynth_points.extend(
            # final_boundary.decode()
        # )

    print(len(accents), " accents left in the list.")
    print(resynth_points)
                

if __name__ == '__main__':
    import sys
    intervals = intervals_from_textgrid(sys.argv[1])
    accents = ['%L', '---', '---', '---', 'H*L', '---', '---', '---', '---', 'L%']
    do_the_stuff(accents, intervals)
