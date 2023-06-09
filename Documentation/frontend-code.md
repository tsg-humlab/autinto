# ToDi Frontend Code

The project's frontend consists of two main parts:
* the course content, which is powered by [mdbook](https://rust-lang.github.io/mdBook/index.html), and
* the exercise widget, which is made using [ReactJS](https://react.dev/).

This document intends to outline important parts of these components and how they work together. It is *not* intended as a usage guide for the website but instead serves as a reference for future developers that may work on this project.

## mdbook
Mdbook is an open source tool specifically used to build 'book' or 'course'-like websites from markdown source files. We chose it as the basis for our website both because it already provides an out-of-the-box working html book website (where we do not have to implement a table of contents or a search feature ourselves), but also because markdown as a file format is a lot more user friendly than html and as such should be easier to work with for our client. More information on how to format using markdown can be found [here](https://rust-lang.github.io/mdBook/format/markdown.html). Note that any html code can also be included directly in markdown.

### Applying changes to the markdown source files
The markdown source files are located in the `uploads/` directory and made to be accessible by the client (via FTP for example). To rebuild the html code from these source files, the `mdbook` command must be executed. This can be done either:
* manually, by running `mdbook build --dest-dir ../static` in the `uploads/` directory,
* by running the `npm run build-book` build script from the `js/` directory, or
* via the website itself, by visiting the `/rebuild_website.html` path.

## The exercise widget
As mentioned before, the exercise widget is built using ReactJS. To add an exercise widget to a page, the following html should be included in the `.md` source file:
```html
<div class="exercise" data-exercise-id="path-to-exercise-specification.json"></div>
```

the React code will hook an instance of the React app onto this `<div>` which will in turn fetch the specification file and then display said exercise.
Both the specification format and the widget itself are built to be as agnostic of the underlying intonation system as possible, in order to be flexible for possible future changes. For example, the exercise JSON file specifies where both the prefilled labels and user choices of labels are located in a sentence, but the React app does not work with their semantics in either parsing the specification file or displaying the exercise to the user. The only part of the widget that does interact with the intonation semantics of the labels is the illegal input handling located in `validate.js`.

### The React state representation
The exercise specification format is optimized for editability, not for the practicality of the exercise widget. As such, the parsing process is quite involved and converts the string representation into a data structure that is easier to work with in Javascript.
The important react states are `exerciseData` and `annotations`.
The latter is a 2D-array of strings, such that for an exercise with `n` sentences, `annotations` will consist of `n` arrays of strings, each of which represents the choices the user has made for the labels that he can select in that sentence.

`exerciseData` is an array that contains the remaining relevant information for each sentence in the exercise. Most notably, the `block` property will contain a list of all the elements in the sentence, which are either
* filler bits of string
* a voiced portion that should not be labeled, represented by an object like this: `{text: '...', choices: null, index: null}`
* a bit of text with a set label that cannot be edited by the user: `{text: '...', choices: 'LABEL', index: null}`
* a bit of text for which the user should select the fitting label: `{text: '...', choices: ..., index: n}`, where the `choices` property is an array of all the allowed opitons and `index: n` specifies that it is the `n`th user-selectable label in the sentence, meaning the choice should be read from / written to `annotaions[item][n]`.

### Integration between the React app and mdbook
In order to hook javascript and css code into the website built by mdbook, one can specify 'additional javascript and css files' in the mdbook config file.
As part of the app's build process (executed via `npm run build`), the `.js` and `.css` files produced by react are copied over to `uploads/additional-files/` and will therfore by included in the website code once the mdbook is built again.
