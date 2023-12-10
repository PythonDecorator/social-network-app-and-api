# social-network-app-and-api

This app allows users to perform CRUD on posts, like, comment, follow, and chat. It also have a fully functioning API
that works exactly as the app and can be integrated easily into any mobile app or used by other developers.

![version](https://img.shields.io/badge/version-1.0.0-blue.svg)

<br />

> Features:

- ✅ `Up-to-date dependencies`
- ✅ `Docker`: Dockerfile and Docker-Compose,
- ✅ `Swagger` Api Documentation
- ✅ `DB Tools`: Django Models, `Django Migrations` (schema migrations),
- ✅ `Persistence`: PostgresSQL (tests, dev and prod)
- ✅ `Authentication`: Session Based, Auth Token
- ✅ `Deployment`: AWS EC2, Render

<br />

## Table of Contents

* [Demo](#demo)
* [Docker Support](#Docker-Support)
* [Reporting Issues](#reporting-issues)
* [Technical Support or Questions](#technical-support-or-questions)
* [Licensing](#licensing)

<br />

## Demo

<br />

## Docker Support

> Get the code

```bash
$ git clone https://github.com/PythonDecorator/social-network-app-and-api.git
$ cd social-network-app-and-api
```

> Run command to build Docker image

```bash
$ docker build .
```

> start server

```bash
$ docker-compose.yaml up
```

> other commands...

```
docker-compose run --rm app sh -c "django-admin startproject app ."
docker-compose run --rm app sh -c "python manage.py test"
docker-compose run --rm app sh -c "python manage.py makemigrations"
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
docker volume ls # to see all the volume active
docker volume rm volume name # to remove a volume
docker-compose up # start server
docker-compose down # stop server
docker-compose run --rm app sh -c "python manage.py createsuperuser"
docker-compose -f docker-compose-deploy.yml down # stop server
docker-compose -f docker-compose-deploy.yml up # start deploy server on server machine
pytest -v --cov=main --cov-report=html  
```

Visit `http://localhost:8000` in your browser. The app should be up & running.

<br />

## Create/Edit `.env` file

The meaning of each variable can be found below:

- `DEBUG`: if `True` the app runs in development mode
    - For production value `False` should be used.
- `username`: ${{ secrets.DOCKERHUB_USER }} your dockerhub username in GitHub secrets
- `password`: ${{ secrets.DOCKERHUB_TOKEN }} your dockerhub token in GitHub secrets

<br />

## Manual Build

> UNZIP the sources or clone the private repository. After getting the code, open a terminal and navigate to the working
> directory, with product source code.

### 👉 Set Up for `Unix`, `MacOS`

> Install modules via `VENV`

```bash
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

<br />

### 👉 Set Up for `Windows`

> Install modules via `VENV` (windows)

```
$ virtualenv venv
$ .\venv\Scripts\activate
$ pip install -r requirements.txt
```

<br />

## Reporting Issues

GitHub Issues IS the official bug tracker for the **social-network-app-and-api**. Here are some advices for users that want
to report an issue:

1. Make sure that you are using the latest version of the **social-network-app-and-api**. Check the CHANGELOG
2. Provide reproducible steps for the issue will shorten the time it takes for it to be fixed.
3. Some issues may be browser-specific, so specifying in what browser you encountered the issue might help.

<br />

## Technical Support or Questions

If you have questions contact me `okpeamos.ao@gmail.com` instead of opening an issue.

<br />

## Licensing

- Copyright 2023 - present [PythonDecorator](https://github.com/PythonDecorator)

<br />

## Social Media

- Twitter: <https://twitter.com/AmosBrymo67154>
- Instagram: <https://www.instagram.com/pythondecorator>

<br />

---
Provided by PythonDecorator



