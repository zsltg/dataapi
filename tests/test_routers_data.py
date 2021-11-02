# pylint: disable=C0114,C0115,C0116
import unittest

from fastapi import testclient

from dataapi import main


class RoutersDataTest(unittest.TestCase):

    _PATH_PREFIX = "/data"
    _DIALOGS = [
        {
            "dialog_id": "1234",
            "customer_id": "janedoe",
            "body": {"text": "The quick brown fox", "language": "EN"},
        },
        {
            "dialog_id": "5678",
            "customer_id": "johndoe",
            "body": {"text": "Springt über den faulen Hund", "language": "DE"},
        },
    ]

    def setUp(self):
        with testclient.TestClient(main.APP) as client:
            self._remove_all_test_dialogs(client)

    def test_create_dialog(self):
        with testclient.TestClient(main.APP) as client:
            # create first dialog, should succeed
            dialog = self._DIALOGS[0]
            response = client.post(
                f"{self._PATH_PREFIX}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 201)
            # create second dialog with same id, should fail
            response = client.post(
                f"{self._PATH_PREFIX}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 409)
            # create third dialog with new id, should succeed
            dialog = self._DIALOGS[1]
            response = client.post(
                f"{self._PATH_PREFIX}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 201)

    def tearDown(self):
        with testclient.TestClient(main.APP) as client:
            self._remove_all_test_dialogs(client)

    @classmethod
    def _remove_all_test_dialogs(cls, client):
        for dialog in cls._DIALOGS:
            client.delete(f"{cls._PATH_PREFIX}/{dialog['dialog_id']}")
