# TODI Frontend
This folder contain the code to both the mdbook (`uploads/`) containing the course text content and the exercise widget source code (`js/`).

## Dependencies
You need to install both [mdbook](https://rust-lang.github.io/mdBook/guide/installation.html) (either prepackaged or built from source) and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Run `npm install` to install all necessary javascript dependencies.

To install all necessary Python dependencies run `pip install -r requirements.txt`

## Build
To build the entire project, run `npm run build` in `js/`.

The full html build can then be found under `static/`.

## Running the server
```
python3 manage.py runserver
```
