
<a href="https://github.com/django/django"><img alt="Uses: Django" src="https://img.shields.io/badge/uses-django-000000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/encode/django-rest-framework"><img alt="Uses: Django REST framework" src="https://img.shields.io/badge/uses-django_rest_framework-00000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/adamchainz/django-cors-headers"><img alt="Uses: Django CORS headers" src="https://img.shields.io/badge/uses-django_cors_headers-000000.svg?style=for-the-badge&color=informational"></a>
<a href="https://github.com/postgres/postgres"><img alt="Uses: PostgreSQL" src="https://img.shields.io/badge/uses-postgreSQL-000000.svg?style=for-the-badge&color=informational"></a>
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
export PATH=$PATH:/usr/pgsql-11/bin:$PATH
alias python3="/usr/local/bin/python3.9"
```
In addition, poetry might require this extra step:
```cli
export PATH="/root/.local/bin:$PATH"
```