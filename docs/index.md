# E.P.I.C.

## About this project (EPIC-Api)
This project is built from the [Django rest framework](https://www.django-rest-framework.org/), based in [Django](https://www.djangoproject.com/), to provide a web API that can interact with different frontends. 

Our current approach connects a [Vue.js](https://vuejs.org/) frontend with this API. The following guides might be helpful to understand the whole set up and coupling process between both tools (kudos to Bennett Garner for these extremely helpful resources):
- [vue+django guide](https://levelup.gitconnected.com/vue-django-getting-started-88d3f4c2ba62)
- [django restapi guide](https://medium.com/swlh/build-your-first-rest-api-with-django-rest-framework-e394e39a482c) 

At the moment we use a [PostgreSQL](https://github.com/postgres/postgres) database to store and manage all the information in a CentOs 7 machine for testing this prototype.

## Purpose
Our goal is to provide organizations with a multi-step questionaire based on their strategic interests which will quickly assess their current situation.

### Reporting
At the moment reporting is only possible as a `.pdf` which is generated by `advisors`, a specific user rol in this tool.

## Contributing
If you wish to contribute to this project we encourage you to have a look at our [contribute guide](docs/guides/contributing.md) or in the [official contributing documentation page](https://deltares.github.io/EPIC-api/guides/contributing)