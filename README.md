# Example App (DataAPI)

## Description

There is a chatbot which process data from our users in real time. There is a background job that pushes the data from the users via HTTP to a data management API (called the DataAPI) so that it gets saved in a database. DataAPI can also be used to retrieve data. Users need to provide an explicit consent to allow their data to be stored and have it managed by the DataAPI.

## Requirements

* `POST /data/${customerId}/${dialogId}`
    * Paylod: `{"text": "the text from the customer", "language": "EN"}`
* `POST /consents/${dialogId}`
    * Payload: `true|false`
    * If `false` it should delete the customer's data
    * Called at the end of a dialog, when the user is asked to give consent
* `GET /data/(?language=${language}|customerId=${customerId})`
    * Return all dialogs...
        * ...which match the query parameters (if any)
        * ...where consent is received (set to `true`)
        * ...sorted by most recent data first
        * ...paginated

## Observations

* `customerId` should uniquely identify a user
* `dialogId` should uniquely identify a dialog
* There should be a one to many relationships between customers and dialogs
    * One customer could have multiple dialogs
    * Since we are storing the dialogs, use the `dialogId` as the unique identifier in the database
* Consent is recorded in a separate call
    * Store the dialog initially with consent received flag set to false
    * Do not return dialogs with false flags
    * When consent is given, set the flag to true
    * When consent is revoked, remove the dialog from the database

# Implementation

## Architecture

<p align="center"><img src="https://github.com/zsltg/dataapi/blob/main/dataapi.png?raw=true" alt="DataAPI Architecture"/></p>

* API in **Python** with **FastAPI** running on **Gunicorn**
* **MongoDB** as the database backend
* Components deployed with **Docker**

### Considerations

* **FastAPI** allows quick, lightweight and standardized way to develop APIs in **Python**
* **Gunicorn** is one of the recommended ways to run **FastAPI** in production
* **MongoDB** is a strongly consistent and partition tolerant database, it has a high read performance which could be an important factor for data analytics work over a large data set

# Usage

## Run

Get Docker: <a href="https://docs.docker.com/engine/install/" class="external-link" target="_blank">https://docs.docker.com/engine/install/</a>

Get Docker Compose <a href="https://docs.docker.com/compose/install/" class="external-link" target="_blank">https://docs.docker.com/compose/install/</a>

### A local version that exposes it ports to the Docker host

* Start
    * `docker-compose -p local -f docker-compose.yml -f docker-compose.local.yml up --build -d`
* Open
    * <a href="http://127.0.0.1:8080/docs" class="external-link" target="_blank">http://127.0.0.1:8080/docs</a>
* Load some test data manually in bulk
    * `pip install poetry`   
    * `poetry install`
    * `PYTHONPATH=. poetry run python scripts/generate_data.py --help`
    * `PYTHONPATH=. poetry run python scripts/generate_data.py -u 100 -d 1000 -c 500`
* Stop
    * `docker-compose -p local -f docker-compose.yml -f docker-compose.local.yml down`
* Teardown
    * `docker-compose -p local kill`
    * `docker-compose -p local rm -f`
    * `docker volume rm local_mongodb local_mongodb_config`

### Integration tests in Docker

* Start
    * `docker-compose -p test -f docker-compose.yml -f docker-compose.test.yml up --build -d`
* Check logs
    * `docker logs dataapi-ui-test`
* Stop
    * `docker-compose -p test -f docker-compose.yml -f docker-compose.test.yml down`
* Teardown
    * `docker-compose -p test kill`
    * `docker-compose -p test rm -f`
    * `docker volume rm test_mongodb test_mongodb_config`

## Develop

* Install Poetry and Tox
    * `pip install poetry tox tox-poetry-installer`   
* Install dependencies
    * `poetry install`
* Add/remove new dependency
    * `poetry add <dependency>`
    * `poetry remove <dependency>`
* Add/remove new development dependency
    * `poetry add --dev <dependency>`
    * `poetry remove --dev <dependency>`
* Run a MongoDB without docker-compose
    * `docker run -p 27017:27017 --name dataapi-db -d mongo:5.0.3`
* Run the UI with Uvicorn
    * `PYTHONPATH=. MONGODB_URL=localhost MONGODB_PORT=27017 poetry run uvicorn main:app --app-dir dataapi --host 0.0.0.0 --port 8080 --reload`
* Spawn a Poetry shell with virtual environment
    * `poetry shell`

Read more about Poetry at: <a href="https://python-poetry.org/" class="external-link" target="_blank">Poetry</a>

## Test

* Run with Tox
    * `tox`
    * `tox -e black`
    * `tox -e pylint`
    * `tox -e mypy`
    * `tox -e pytest`
* You can also run these through Poetry, for example...
    * `poetry run black --check --diff dataapi tests`

# Additional Notes

* I added some extra API endpoints (on top of what was described in the requirements) to help with integration testing
    * `GET /data/{customerId}/{dialogId}`
    * `DELETE /data/{customerId}/{dialogId}`
* For this limited example I created some integration tests
    * I felt like these provide the most value as these are more closely mimic real word usage over other type of tests
    * These don't cover the whole code base, so additional tests can be added later
    * See an example at the end how Unit tests can be potentially added for the async functions
    * Mutation testing could be used improve the test coverage
        * In fact, one of the Python mutation testing tool, **mutmut** is included in the project
        * This is not included in the test suite by default, since the current coverage is low
        * `tox -e mutmut`

# Going forward

* Add versioning to the API?
* Recording a dialog and a consent is a two-step process
    * Can it happen that the upstream system never sends a consent and dialogs become stale?
    * Consider running a clean up job periodically to remove stale dialogs from the system?
* Add logging and monitoring
* Scaling
    * This is a very limited deployment at the moment with one web server and a database
    * Both the web servers and the database backend could be extended to accomodate more traffic
    * A caching layer could be introduced to ease the load on the backend
    * The web servers could run independently from each other with a load balancer in front and the databases could run in a cluster
* Input validation
    * With more clarification about the requirements and the structure of the data we could add stricter input validation to ensure better data quality
* Security
    * Authentication and authorization needs to be added to prevent unauthorized use
    * Downstream users and applications with different roles could access different endpoints and perform different actions
    * Encryption can be introduced to protect sensitive data (personal information about the user, dialog content)

## Example Unit test for async functions

```
import unittest
from unittest import mock
from functools import wraps
import asyncio
import pymongo

from dataapi.controllers import dialog_controller


def async_test(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        args[0].loop.run_until_complete(function(*args, **kwargs))

    return wrapper


class AsyncMock(mock.MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class DialogControllerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.get_event_loop()

    @async_test
    async def test_create_dialog(self):
        database = AsyncMock()
        database.chatbot.dialog.insert_one.side_effect = (
            pymongo.errors.DuplicateKeyError("")
        )
        result = await dialog_controller.create_dialog(database, mock.MagicMock())
        self.assertEqual(result.status_code, 409)

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()
```
