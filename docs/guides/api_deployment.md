## Table of contents
* [EpicApi deployment](#EpicApi-deployment)
    * [Checking requirements](#checking-requirements)
    * [Installing Django](#installing-django)
    * [Gunicorn run](#gunicorn-run)
    * [NGINX configuration](#nginx-configuration)
* [Development setup](#development-setup)
* [Production setup](#production-setup)

# EpicApi deployment
To deploy the backend in an open environment we recommend following [Django guidelines](https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/gunicorn/) by using [gunicorn](https://docs.gunicorn.org/en/latest/install.html) and [NGINX](https://www.nginx.com/).

The following requirements should be met:

* UNIX system.
* NGINX. Already installed and configured.
* SQLite. At least version 3.9
* Python. At least version 3.8

Are you deploying on a CentOs machine? You can follow the [CentOs installation steps](#installing-on-a-centos-machine) for SQLite and Python in the [appendix section](#appendix).

## Checking requirements 
It could be possible that your UNIX system does not have the latest python and/or SQLite versions. Please ensure you have installed Python (at least) 3.8 and SQLite (at least) 3.9.
To check it do the following:
```cli
python3
>> import sqlite3
>> sqlite3.sqlite_version
```
> * The first line will prompt us into the python3 CLI. Right below the executed line we will be able to see the current version of our Python3.
> * The third line will display the associated version of SQLite with our Python build.
>   * If it does not return the expected value then we recommend recompiling your python binaries.

## Installing Django

* Checkout the root directory of the EPIC-api repository somewhere recognizable. Such as /var/www/epicapi-site/.
* Navigate with the commandline to the previous checkout directory.
* Define debug and secret key values:
    * Create a secret key through Python CLI
        ```cli
        python
        >> import secrets
        >> from pathlib import Path
        >> Path('.django_secrets').write_text(secrets.token_hex(16))
        ```
        > A new file is now generated containing your unique token key expected by /epic_core/settings.py. In case this key is not valid please contact carles.sorianoperez@deltares.nl to provide a valid one.
    * Define a debug value:
        * For development:
            ```cli
            python
            >> from pathlib import Path
            >> Path('.django_debug').write_text("True")
            ```
        * For production:
            ```cli
            python
            >> from pathlib import Path
            >> Path('.django_debug').write_text("False")
            ```
* Install now the current Django package.
    ```cli
    poetry install
    poetry run python3 manage.py collectstatic --noinput
    ```
    * Alternative with latest pip versions:
        ```cli
        pip install -e .
        python3 manage.py collectstatic --noinput
        ```
        > It will install the .toml package in edit mode.
* Run our custom command to create the database and add an admin user:
    * For development:
        ```cli
        poetry python manage.py epic_setup --test
        ```
        > This will import all initial data and generate a test admin user (admin-admin) and several test 'EpicUsers'.
    * For production:
        ```cli
        poetry python manage.py epic_setup
        ```
        > This will import all initial data but WILL NOT generate a default admin user, you will have to create it yourself.
        ```cli
        poetry run python manage.py createsuperuser
        ```
        * If desired you can change the password after creating the user by running: 
            ```cli
            poetry run python manage.py changepassword <admin username>
            ```

* The tool is now ready to run. In our case we will do it with Gunicorn on the next section.

## Gunicorn run:

If we have not executed the custom script, then we need to run on a separate process gunicorn, we only need to execute the following command line as a background activity:
```cli
    poetry run gunicorn epic_core.wsgi
```
    > An output in the command line will show you where the (local) server is deployed. By default you should be able to check its functioning here: http://127.0.0.1:8000/ 

## NGINX configuration:
Although we are already 'serving' our Django applicaiton, this does not mean that it is accessible outside our local machine.
Most likely you will require to do a redirection of the requests to the backend. For that it's necessary adding the following lines into your 'nginx' .conf file:
```conf
server {
    ...
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ^~ /admin/ {
        proxy_pass http://127.0.0.1:8000/admin/;
        proxy_set_header Host      $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
Now our NGINX server will be able to redirect our http calls to our application. As a last step, restart the NGINX server:
```cli
sudo systemctl restart nginx
```
