If you wish to contribute to this project you may want to get familiar with our tooling. We strongly advise to get familiar with the following tools:

- [poetry](https://python-poetry.org/) for package handler.
- [black](https://black.readthedocs.io/en/stable/) for code styling.
- [isort](https://github.com/PyCQA/isort) for code styling.
- [commitizen](https://commitizen-tools.github.io/commitizen/) for version control.
- [pytest](https://github.com/pytest-dev/pytest) for ensuring continuous integration of the tool.

# Getting your development environment ready.
## Using pip
Using `pip` in its latest version allows us to install the .toml file in edit mode. Keep in mind you will have to be running with python 3.8 (at least).
```bash
cd /epic-api
pip install -e .
```

## Using poetry

```bash
cd /epic-api
pip install poetry
poetry install
poetry run
```

## Using conda
Regardless of installing through pip or poetry, we will still need to create our custom conda environment:
```bash
cd /epic-api
conda create --name epicapi_env python=3.8
conda activate epicapi_env
```
* With pip
    ```bash
    pip install -e .
    ```

* With poetry:
    ```bash
    poetry install
    poetry run
    ```
    > __Important:__ it turns out if you work with conda as a python environment you may come against a compatibility problem with virtualenv, we therefore recommend downgrading the pre-installed package of virtualenv of poetry to 20.0.3.
    ```bash
    conda install poetry
    conda install virtualenv==20.0.33
    poetry install
    poetry run
    ```

You should have now all the dependencies, including django and djangorestframework as they are defined in the `pyproject.toml` file, installed in our environment.

# Some development rules.

## Branches

Each new feature, fix, documentation, pipeline, depencencies, etc, that need to be updated will be done in their own branch. We try to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/), as a general rule, we work with the following branch naming:

* __master__: Protected, further reading in section "[Merging into master](#merging-into-master)".
* __develop__: Can be created if not present in order to 'cluster' commits related to a specific version.
* __feat/feature_descriptive_name__: When working on a new feature.
* __chore/chore_description__: When doing some chores in the project such as clean-up of unnecessary files, minor refactorings and so on.
* __docs/documentation_description__: When adding or modifying documentation in the repository.
* __fix/name_of_the_fix__: When trying to fix a specific issue / bug in the project.
* __ci/name_of_the_task__: When working on anything related to the project dependencies (poetry / .toml) or the pipelines (.github/workflows).

## Commiting
A pre-commit hook is present in this repository and the package should have been installed from the .toml file. In this repository we try to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) convention. Which is further enforced by the usage of `commitizen`.

### Commitizen version control
When doing a pull-request we encourage to run the `cz bump --changelog` command which will potentially update the tool version number as well as the `changelog` file. If this happens, you should also push the new git tags with `git push --tags`.

## Testing
Testing is fulfilled with the usage of `pytest`. Most of the tests are located in `epic_app/tests` directory. Said test directory 'mirrors' the epic_core structure. So whenever a new file is introduced a new test file should be created. Example given:

```
/epic-api
    |- /epic-core
    |   |- /tests
    |   |   |- __init__.py
    |   |   |- /models
    |   |   |   |- __init__.py
    |   |   |   |- test_new_model.py
    |   |- /models
    |   |   |- __init__.py
    |   |   |- new_model.py
```

As a general rule of thumb, if code is created or modified, the test bench should be updated with `unit tests` to cover that new / modified piece of code.

When a new workflow is introduced, e.g. routes, it is highly encourage to create a system test that will evaluate the final expected values. For more information on how to achieve this please contact the project administrator.

## Merging into master
Merging into `master` needs to be done through a pull-request. Please ensure the following steps are fulfilled:

- Tests are updated and/or extended.
- The code is correctly formatted.
- Documentation is added.
    - Docstrings for code, using the [google docs](https://google.github.io/styleguide/pyguide.html) format.
    - [Type hinting](https://docs.python.org/3/library/typing.html) in all methods (in and out).
    - Markdown files in /docs when workflows or project / architectural changes have been introducing.
- [Commitizen has been run](#commitizen-version-control) to check for version bumping.
- GitHub Pipelines succeed.

## Updating EpicTool models.
During development it is natural to create new tables or define new columns on a database entry. The most important is to manage the Django migrations with the following steps:
```bash
python manage.py makemigrations
python manage.py migrate
```
The new migrations should be included in the version control as the production server (as well as other contributors) will require them in order to preserve their existing database data.

Also, keep in mind that if a new entity needs to be modified through the Django Admin page it will also have to be added into the admin.py page.

# Licensing
At the moment of writing of this document we have an [MIT](https://opensource.org/licenses/MIT) license. It is not intended to include packages or tools which require a more restrictive license or a payment in any form.