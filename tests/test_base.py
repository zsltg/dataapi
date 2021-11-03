# pylint: disable=C0114,C0115,C0116
import unittest
import datetime
import uuid
import random
import string

from fastapi import encoders
import pymongo
from lorem_text import lorem

from dataapi import config
from dataapi.models import dialog_model


class BaseTest(unittest.TestCase):

    _settings = config.get_settings()
    _client = pymongo.MongoClient(_settings.mongodb_url, int(_settings.mongodb_port))
    _db = _client.chatbot.dialog
    _data_path_prefix = "/data"
    _consent_path_prefix = "/consents"
    _languages = ["EN", "DE", "IT", "FR"]
    _on_demand_dialogs = []
    _bulk_customer_count = 10
    _bulk_dialog_count = 1000
    _bulk_consent_count = 500

    def setUp(self):
        self._db.delete_many({})
        for dialog in self._generate_dialogs(10, 2, self._languages):
            self._on_demand_dialogs.append(dialog)
        for dialog in self._generate_dialogs(
            self._bulk_customer_count, self._bulk_dialog_count, self._languages
        ):
            self._db.insert_one(dialog)
        cursor = self._db.find().limit(self._bulk_consent_count)
        for entry in cursor:
            self._db.update_one(
                {"_id": entry["_id"]}, {"$set": {"consent_received": True}}
            )

    def test_pass(self):
        pass

    def tearDown(self):
        # self._db.delete_many({})
        pass

    def _create_dialogs_with_one_consent(self, client):
        # create some new dialogs
        for dialog in self._on_demand_dialogs:
            client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
                json=self._get_dialog_request_body(dialog),
            )
        # record consent for first dialog
        dialog = self._on_demand_dialogs[0]
        response = client.post(
            f"{self._consent_path_prefix}/{dialog['_id']}",
            data="true",
        )
        return response

    @classmethod
    def _get_dialog_request_body(cls, dialog):
        return {"text": dialog["text"], "language": dialog["language"]}

    @classmethod
    def _generate_customer_id(cls):
        return "".join(
            random.choice(string.ascii_lowercase) for i in range(random.randint(5, 10))
        )

    @classmethod
    def _generate_dialog(cls, customer_id, language):
        return encoders.jsonable_encoder(
            dialog_model.DialogModel(
                customer_id=customer_id,
                dialog_id=str(uuid.uuid4()),
                text=lorem.sentence(),
                language=language,
                date=datetime.datetime.utcnow(),
            )
        )

    @classmethod
    def _generate_dialogs(cls, customer_count, dialog_count, languages):
        customers = [cls._generate_customer_id() for _ in range(customer_count)]
        for _ in range(dialog_count):
            yield cls._generate_dialog(
                random.choice(customers), random.choice(languages)
            )
