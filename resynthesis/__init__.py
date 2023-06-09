"""
The resynthesis module determines new frequency targets for the
resynthesized sentence, and duration changes, and uses Praat to perform
resynthesis.
"""

import os.path
import subprocess
import time

from resynthesis.phrase import Phrase
from resynthesis.resynthesized import ResynthesizedPhrase

import textgrid as tg

def resynthesize(sentence, textgrid_filename, audio_filename, **kwargs):
    """
    This is the main function. It expects:
      1. A sentence in the form of: [accent, ..., accent], with accent a
         string, or None where there is no accent;
      2. A corresponding TextGrid filename;
      3. A corresponding WAV file filename;
      4. Any optional global arguments. Valid arguments are the
         variables in ResynthesizeVariables in `types.py`.

    We resynthesize the phrase and decode it into a TextGrid, let Praat
    handle it and then return the output as two bytes objects: the new
    WAV file and a visual representation in SVG format.
    """

    # create a Phrase from the textgrid, then a ResynthesizedPhrase from
    # the Phrase and the sentence, and get the new textgrid from that
    phrase = Phrase(textgrid_filename)
    resynth_phrase = ResynthesizedPhrase(phrase, sentence, **kwargs)
    resynth_textgrid = resynth_phrase.decode_into_textgrid()

    # send that to praat
    (new_audio, pdf_image) = send_to_praat(audio_filename, resynth_textgrid)

    # and convert the image
    svg_image = pdf_to_svg(pdf_image)

    return (new_audio, svg_image)


def send_to_praat(audio_filename, resynthesized_textgrid):
    """
    Here we convert the audio and modified TextGrid files to a Praat
    call and send it to Praat. It returns the bytes of a WAV and a PDF
    file.
    """

    # Make unique temp filenames
    prefix = '/tmp/todi-resynth-{}'.format(time.time_ns())
    tg_tmp = '{}.TextGrid'.format(prefix)
    wav_tmp = '{}.wav'.format(prefix)
    pdf_tmp = '{}.pdf'.format(prefix)


    # praat & praat script are in same folder as this file, so we find
    # that folder and then the script:
    resynthesis_dir = os.path.dirname(__file__)
    praat_exec = os.path.join(resynthesis_dir, 'praat_nogui')
    praat_script = os.path.join(resynthesis_dir, 'resynth.praat')

    # write the textgrid to a temp file:
    resynthesized_textgrid.write(tg_tmp)

    # Here we make the actual call to praat
    subprocess.run([praat_exec,
                    '--run',
                    praat_script,
                    audio_filename,
                    tg_tmp,
                    wav_tmp,
                    pdf_tmp],
                   timeout=10) # seconds

    # We open the temp files so we can return the contents
    # Named pipes were used originally instead of files, but had trouble
    # with hanging unpredictably.
    with open(wav_tmp, 'rb') as f:
        wav_out = f.read()

    with open(pdf_tmp, 'rb') as f:
        pdf_out = f.read()

    # remove the temporary files again
    os.unlink(tg_tmp)
    os.unlink(wav_tmp)
    os.unlink(pdf_tmp)

    return (wav_out, pdf_out)

def pdf_to_svg(pdf_bytes):
    """
    This function converts a PDF in bytes to an SVG image in bytes.
    """
    completed_process = subprocess.run(['pdftocairo', '-svg', '-', '-'],
                                       input=pdf_bytes,
                                       stdout=subprocess.PIPE)

    return completed_process.stdout
