# bebleo: Checklist

Checklist is a proof-of-concept for a solution that allows users to create, update, and delete lists and to track the changes that are made. It is not a production-ready site. If you're looking for one, I suggest searching for something else.

Branch | Build
-------|------
master | [![Build Status](https://travis-ci.com/bebleo/checklist.svg?branch=master)](https://travis-ci.com/bebleo/checklist)
dev | [![Build Status](https://travis-ci.com/bebleo/checklist.svg?branch=dev)](https://travis-ci.com/bebleo/checklist)

## Introduction

The making of checklist has been primarily motivated by a desire to produce a todo list solution that extends beyond the normal to-do list and the design considerations that come in to play.

It's also an opportunity to work in python and to experiment with:

- Flask
- Flask-Mail
- Flask-SQLAlchemy
- Flask-WTF

Users may notice that a lot of the material in the site derives heavily from the Flask tutorial and the quickstarts for the above projects. This is freely and gratefully acknowledged.

### Running the Sample

The checklist site can be run using the built-in Flask development server for the first-time byby setting up a virtual environment and installing the depencies. To install it in the current directory:

```shell
pip install -e .
```

You will then be able to initialize the database and run the application:

```shell
export FLASK_ENV=development
export FLASK_APP=checklist_app
flask init-db
flask run
```

Or, on windows:

```shell
set FLASK_ENV=development
set FLASK_APP=checklist_app
flask init-db
flask run
```

After the first run, unless there is a need to reinitialize the database the command `flask init-db` should be omitted.

## Contributors

This project isn't currently seeking any contributors.

-----

Copyright 2019-2020. Written with ❤ and ☕ in Montréal, QC
