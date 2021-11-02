# pylint: disable=C0114,C0115,C0116
import unittest

from fastapi import testclient

from dataapi import main


class BaseTest(unittest.TestCase):

    _data_path_prefix = "/data"
    _consent_path_prefix = "/consents"
    _dialogs = [
        {
            "dialog_id": "123453697821-b204-474d-b646-d8702690381e",
            "customer_id": "janedoe",
            "body": {"text": "The quick brown fox", "language": "EN"},
        },
        {
            "dialog_id": "123522037567-ad6b-441c-8e28-25f3c9e4558b",
            "customer_id": "janedoe",
            "body": {"text": "Jumps over the lazy dog", "language": "EN"},
        },
        {
            "dialog_id": "56781f4e9adb-d343-4129-8e2d-435387d16c7f",
            "customer_id": "johndoe",
            "body": {"text": "Der schnelle braune Fuchs", "language": "DE"},
        },
        {
            "dialog_id": "567969636056-d26a-4785-b828-b145c0c62144",
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
