# TODI Frontend
This folder contain the code to both the mdbook (`uploads/`) containing the course text content and the exercise widget source code (`js/`).

## Dependencies
You need to install both [mdbook](https://rust-lang.github.io/mdBook/guide/installation.html) (either prepackaged or built from source) and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

Run `npm install` to install all necessary javascript dependencies.

To install all necessary Python dependencies run `pip install -r requirements.txt`

Lastly, the project needs a Praat executable. This project has been tested with Praat version [6.3.10](https://github.com/praat/praat/releases/v6.3.10/). In particular, it *will not work* on Praat version 6.2.
When installing, be sure to put the **nogui** version of Praat in the [resynthesis](resynthesis/) folder, with the name `praat_nogui`. The executable used in development can be found [here](https://github.com/praat/praat/releases/download/v6.3.10/praat6310_linux64nogui.tar.gz).

## Build
To build the entire project, run `npm run build` in `js/`.

The full html build can then be found under `static/`.

## Running the server
```
python3 manage.py runserver
```

## Setting up the SFTP server
To set up the SFTP server, follow [this](https://www.techrepublic.com/article/how-to-set-up-an-sftp-server-on-linux/) tutorial and use the uploads folder as directory for the server. Change users and permissions the way you like. You can then connect to it over SSH by either using a client like [filezilla](https://filezilla-project.org/) or by using the `sftp` command.

## Setting up Nginx
To set up Nginx, follow [this](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html) tutorial and use the todi folder as Django project and the corresponding paths on your system. Also uWSGI is needed but that is explained in the tutorial.
