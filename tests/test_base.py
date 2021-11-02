# pylint: disable=C0114,C0115,C0116
import unittest

from fastapi import testclient

from dataapi import main


class BaseTest(unittest.TestCase):

    _data_path_prefix = "/data"
    _consent_path_prefix = "/consents"
    _dialogs = [
        {
            "dialog_id": "1234",
            "customer_id": "janedoe",
            "body": {"text": "The quick brown fox", "language": "EN"},
        },
        {
            "dialog_id": "1235",
            "customer_id": "janedoe",
            "body": {"text": "Jumps over the lazy dog", "language": "EN"},
        },
        {
            "dialog_id": "5678",
            "customer_id": "johndoe",
            "body": {"text": "Der schnelle braune Fuchs", "language": "DE"},
        },
        {
            "dialog_id": "5679",
            "customer_id": "johndoe",
            "body": {"text": "Springt über den faulen Hund", "language": "DE"},
        },
    ]

    def setUp(self):
        with testclient.TestClient(main.app) as client:
            self._remove_all_test_dialogs(client)

    def tearDown(self):
        with testclient.TestClient(main.app) as client:
            self._remove_all_test_dialogs(client)

    @classmethod
    def _remove_all_test_dialogs(cls, client):
        for dialog in cls._dialogs:
            client.delete(
                f"{cls._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}"
            )
