# Making a web request

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
