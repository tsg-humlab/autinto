# TODI Frontend
This folder contain the code to both the mdbook (`book/`) containing the course text content and the exercise widget source code (`exercise-widget/`).

## Dependencies
You need to install both [mdbook](https://rust-lang.github.io/mdBook/guide/installation.html) (either prepackaged or built from source) and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Run `npm install` inside the `exercise-widget/` folder.

## Build
The exercise widget should be built first, by running
```
npm run build
```
inside `exercise-widget/`.

Thereafter, we can build the mdbook by running
```
mdbook build
```
inside `book/`.

The full html build can then be found under `book/build/`.

### Development
During development, you might want the builds to rerun automatically whenever the underlying source files change. For this purpose you can use
```bash
mdbook serve --open
```
```bash
npm start
```
instead of the commands given above.