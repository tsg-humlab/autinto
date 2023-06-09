# ToDI Resynthesis

## Structure

### What to edit

The rules for the targets for Words, Initial Boundaries, and Final Boundaries are in [`pitch_accents.py`](pitch_accents.py). You should be able to make most changes there. To see the abstractions that these have access to, like `self.next_word` and `self.scale_frequency()`, take a look at [`abstract_pitch_accents.py`](abstract_pitch_accents.py).

It’s also helpful to review [`types.py`](types.py), mainly to see the definitions of `Interval`s, global variables (`ResynthesizeVariables`), and the classes that define new frequency and duration targets for Praat (`FrequencyPoint` and `AddTime` respectively).

Those files should be enough to perform most changes; in particular, editing `pitch_accents.py` should be all one needs to do to add or modify resynthesis rules (or replacing `pitch_accents.py` altogether, in the case of completely different pitch accents!)

### Complete overview

This is a Django module; `admin.py`, `apps.py`, `models.py`, `tests.py`, `urls.py`, and `views.py` were all created by Django. Most of these files don’t contain anything, with two exceptions: `urls.py`, which points to `views.py`, and `views.py`, which handles the web request and calls the actual resynthesis.

That leaves `__init__.py`, `abstract_pitch_accents.py`, `phrase.py`, `pitch_accents.py`, `resynthesized.py`, `resynth.praat`, and `types.py` as the files performing the actual resynthesis. They each contain docstrings and comments about what goes on inside them, but here’s a quick reference for what they all do:

| Filename | Description |
| -------- | ----------- |
| [`pitch_accents.py`](pitch_accents.py) | <p>**This is, hopefully, the only file you will have to edit if you don’t want to make integral changes to the structure, and only want to change the resynthesis rules.** <p>If you want to edit the behaviour of certain words, you should look into `pitch_accents.py`. It defines three important classes, Word, InitialBoundary, and FinalBoundary, which create the frequency targets for each pitch accent. |
| [`abstract_pitch_accents.py`](abstract_pitch_accents.py) | If you want to alter (or look into) the abstractions available for the pitch accents, then take a look at `abstract_pitch_accents.py`. Features like calling `self.next_word` on a Word are defined here. |
| [`phrase.py`](phrase.py) | This file contains the interpreting of TextGrid files. It defines a `Phrase`, `IntonationalPhrase`, and `VoicedPortion` class. Each of these are intervals, with a start and end time. A Phrase contains one or more IntonationalPhrases, which all contain one or more VoicedPortions. |
| [`resynthesized.py`](resynthesized.py) | This file contains the classes `ResynthesizedPhrase` and `ResynthesizedIntonationalPhrase`. A `ResynthesizedPhrase` is essentially a combination of a `Phrase` (created from a TextGrid) and a user-inputted sentence. The creation of the frequency targets is then performed by calling `decode()` on this `ResynthesizedPhrase`. |
| [`types.py`](types.py) | <p>This file defines some features that many other files use, like the `Milliseconds` function, and the `Interval` class. <p>Also in here are the global variables: they are contained in `ResynthesizeVariables`, which includes FROMTIME, STARTIME, Fr, N, W, and others. Their default values can be modified here, but note that the default frequencies are overridden by gender somewhere else; this is further explained in `types.py`. |
| [`__init__.py`](__init__.py) | Here the `resynthesize()` function is defined, which calls everything else, and thus performs the entire resynthesis (including calling Praat and generating a new audio file & image). Sending the modified TextGrid to Praat is also done here, as is converting the returned PDF file into an SVG that can be displayed as an image in the webbrowser. If you want to trace the entire program flow (excluding the web request), this is where to start. |
| [`views.py`](views.py) | `views.py` transforms the input from a POST request into a format that the module will understand, and transforms the module’s output back into a JSON file that the client will read. If you want to trace the entire program flow *in*cluding the web request, this is where to start. |
| [`resynth.praat`](resynth.praat) | This is the Praat script that is used for the actual resynthesis. Hopefully this will never need to be changed, but it performs the creation of the new WAV file and the creation of the contour image as a PDF file. |

## Running this code

### Running from Python

This folder works as a Python module. To test it from the command line, go up to the root folder of this project, and do:

```python
from resynthesis import resynthesize
(audio, svg) = resynthesize(['%L', None, 'H*L', None, None, None, None, None, 'L%'],
                            'static/1_falling_contours/TextGrid/1A-1.TextGrid',
                            'static/1_falling_contours/wav/1A-1.wav')
```

### Making a web request

Should work by making a POST request to http://{server}/resynthesize/, with three body elements:

* `sentence`, containing the pitch accents formatted as a JSON string. All empty elements are `null`. Example:

  ```["%L", null, "H*L", null, null, null, null, null, "L%"]```

* `wav`, containing the location of the wav file to be resynthesized (from the static/ directory)

* `TextGrid`, containing the location of the TextGrid

Example curl command to test:

```bash
curl -Ss -X POST \
-F 'sentence=["%L", null, "H*L", null, null, null, null, null, "L%"]' \
-F 'wav=1_falling_contours/wav/1A-1.wav' \
-F 'TextGrid=1_falling_contours/TextGrid/1A-1.TextGrid' \
'http://localhost:8000/resynthesize/'
```
