# ToDI Resynthesis

## Structure

This is a Django module; `admin.py`, `apps.py`, `models.py`, `tests.py`, `urls.py`, and `views.py` were all created by Django. Most of these files don’t contain anything, with two exceptions: `urls.py`, which points to `views.py`, and `views.py`, which handles the web request and calls the actual resynthesis.

`views.py` transforms the input into a format that the module will understand, and transforms the module’s output back into a JSON file that the client will read.

That leaves `__init__.py`, `abstract_pitch_accents.py`, `phrase.py`, `pitch_accents.py`, `resynthesized.py`, `resynth.praat`, and `types.py` as the files performing the actual resynthesis. They each contain docstrings and comments about what goes on inside them, but here’s a quick reference for what they all do:

* If you want to edit the behaviour of certain words, you should look into `pitch_accents.py`. It defines three important classes, Word, InitialBoundary, and FinalBoundary, which create the frequency targets for each pitch accent.
* If you want to alter (or look into) the abstractions available for the pitch accents, then take a look at `abstract_pitch_accents.py`. Features like calling `self.next_word` on a Word are defined here.


## Running this code

### Running from Python

This folder works as a package. To test it from the command line, go up to the root folder of this project, and do:

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
