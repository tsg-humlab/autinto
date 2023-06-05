import os.path
import subprocess
import time

from resynthesis.phrase import Phrase
from resynthesis.resynthesized import ResynthesizedPhrase

import textgrid as tg

def resynthesize(sentence, textgrid_filename, audio_filename, **kwargs):
    phrase = Phrase(textgrid_filename)
    resynth_phrase = ResynthesizedPhrase(phrase, sentence)
    resynth_textgrid = resynth_phrase.decode_into_textgrid()

    (new_audio, pdf_image) = send_to_praat(audio_filename, resynth_textgrid)
    svg_image = pdf_to_svg(pdf_image)

    return (new_audio, svg_image)


def send_to_praat(audio_filename, resynthesized_textgrid):
    # Make unique temp filenames
    prefix = '/tmp/todi-resynth-{}'.format(time.time_ns())
    tg_tmp = '{}.TextGrid'.format(prefix)
    wav_tmp = '{}.wav'.format(prefix)
    pdf_tmp = '{}.pdf'.format(prefix)


    # praat script is in same folder as this file, so we find that
    # folder and then the script:
    resynthesis_dir = os.path.dirname(__file__)
    praat_script = os.path.join(resynthesis_dir, 'resynth.praat')

    resynthesized_textgrid.write(tg_tmp)

    subprocess.run(['praat',
                    '--run',
                    praat_script,
                    audio_filename,
                    tg_tmp,
                    wav_tmp,
                    pdf_tmp],
                   timeout=10) # seconds

    with open(wav_tmp, 'rb') as f:
        wav_out = f.read()

    with open(pdf_tmp, 'rb') as f:
        pdf_out = f.read()

    # cleanup
    os.unlink(tg_tmp)
    os.unlink(wav_tmp)
    os.unlink(pdf_tmp)

    return (wav_out, pdf_out)

def pdf_to_svg(pdf_bytes):
    completed_process = subprocess.run(['pdftocairo', '-svg', '-', '-'],
                                       input=pdf_bytes,
                                       stdout=subprocess.PIPE)

    return completed_process.stdout
