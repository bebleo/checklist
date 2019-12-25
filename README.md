# checklist

Checklist should be considered a proof-of-concept for a solution that allows users to create, update, and delete lists and to track the changes that are made. As such the aim is not to produce a production-ready site. If you're looking for one we suggest searching for a production ready site.

## Introduction

The making of checklist has been primarily motivate by a desire to produce a todo list solution that extends beyond the normal to-do list and the design considerations that come in to play.

It's also an opportunity to work in python and to experiment with:

- Flask
- Flask-Mail
- Flask-WTF

Users may notice that a lot of the material in the site derives heavily from the Flask tutorial. This is freely and gratefully acknowledged.

### Running the Sample

The checklist site can be run using the built-in Flask development server for the first-time by:

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

Copyright 2019. Written with :heart: and :coffee: in Montréal, QC
