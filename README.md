
<a href="https://github.com/django/django"><img alt="Uses: Django" src="https://img.shields.io/badge/uses-django-000000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/encode/django-rest-framework"><img alt="Uses: Django REST framework" src="https://img.shields.io/badge/uses-django_rest_framework-00000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/adamchainz/django-cors-headers"><img alt="Uses: Django CORS headers" src="https://img.shields.io/badge/uses-django_cors_headers-000000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge"></a>

### Table of contents

* [About EPIC-Tool](#about-epic-tool-backend)
* [Collaborationg](#collaborating)
    * [Getting your development environment ready](#getting-your-development-environment-ready)
* [Updating EpicTool models](#updating-epictool-models)
* [Appendix](#appendix)
    * [Invoking the libraries](#invoking-the-libraries)

## About EPIC-Tool backend
The EPIC-Tool backend uses [Django](https://www.djangoproject.com/), a python web framework, which will be used by the frontend as an API.
For the current approach (Django + Vue) we will follow an approach similar to the one described in the following [vue+django guide](https://levelup.gitconnected.com/vue-django-getting-started-88d3f4c2ba62), and [django restapi guide](https://medium.com/swlh/build-your-first-rest-api-with-django-rest-framework-e394e39a482c) kudos to Bennett Garner for these extremely helpful resources.

## Collaborating
If you wish to collaborate on this project you may want to get familiar with our tooling. In this project the following packages are used:
* [poetry](https://python-poetry.org/) for package handler.
* [black](https://black.readthedocs.io/en/stable/) for code styling.
* [commitizen](https://commitizen-tools.github.io/commitizen/) for version control.

### Getting your development environment ready.
* Using pip:
    ```
    pip install poetry
    poetry install
    poetry run
    ```
* Using conda:
    > Note: it turns out if you work with conda as a python environment you may come against a compatibility problem with virtualenv, we therefore recommend downgrading the pre-installed package of virtualenv of poetry to 20.0.3.
    ```
    conda install poetry
    conda install virtualenv==20.0.33
    poetry install
    poetry run
    ```

You should have now all the dependencies, including django and djangorestframework, installed in our environment.


## Updating EpicTool models.
During development it is natural to create new tables or define new columns on a database entry. The most important is to manage the Django migrations with the following steps:
```cli
python manage.py makemigrations
python manage.py migrate
```
Also, keep in mind that if a new entity needs to be modified through the Django Admin page it will also have to be added into the admin.py page.


## Appendix
### Invoking the libraries:
To ensure everything gets picked up correctly you can execute the following command lines:
```cli
export LD_LIBRARY_PATH="/usr/local/lib/"
PATH=$PATH:/usr/local/bin
alias sqlite3="/usr/local/bin/sqlite3"
alias python3="/usr/local/bin/python3.9"
```
In addition, poetry might require this extra step:
```cli
export PATH="/root/.local/bin:$PATH"
```