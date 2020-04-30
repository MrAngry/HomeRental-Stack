# Damian Kuna-Broniowski

## Introduction

The project was created with a few assumptions:
   - `isDeleted` field can be set in `POST` method
   - `isImported` field can be set in `POST` method
   -  `time` field was omitted as no explanation to its meaning was given

## Setup

*Pre-requisites:*
- Python 3.7+

### Required dependencies

To install Python dependencies, run the following commands:

```
python3 -m venv venv
. ./venv/bin/activate
pip install -r ./requirements.txt
python manage.py makemigrations
python manage.py migrate
```

### Project 
There is one Django app here:`payments`. The project uses by default SQLite as backend DB this can be changed by setting appropriate values in `settings.py`

- you can run it by:
 
  ```
  python manage.py runserver 3000
  ```
  which will make the server available at http://127.0.0.1:3000


### Tests
The tests are located in `payments\tests` folder
- you can run unittest for the whole project by:
```
python manage.py test
```

