from resynthesis.phrase import Phrase
from resynthesis.resynthesized import ResynthesizedPhrase

import textgrid as tg

def resynthesize(sentence, textgrid_filename, audio_filename, **kwargs):
    phrase = Phrase(textgrid_filename)
    resynth_phrase = ResynthesizedPhrase(phrase, sentence)
    resynth_points = resynth_phrase.decode()

    resynthesized_textgrid = update_textgrid(textgrid_filename, resynth_points)


def send_to_praat(audio_filename, resynthesized_textgrid):
    pass


def update_textgrid(textgrid_filename, resynth_points) -> tg.TextGrid:
    grid = tg.TextGrid.fromFile(textgrid_filename)
