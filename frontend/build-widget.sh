#!/bin/sh
(cd exercise-widget && npm run build)
cp ./exercise-widget/build/static/js/main.*.js ./book/additional-files/main.js
cp ./exercise-widget/build/static/css/main.*.css ./book/additional-files/main.css
