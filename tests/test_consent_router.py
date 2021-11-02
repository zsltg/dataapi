# pylint: disable=C0114,C0115,C0116
import json
from fastapi import testclient

from dataapi import main
from tests import test_base


class RoutersDataTest(test_base.BaseTest):
    def test_record_consent(self):
        with testclient.TestClient(main.app) as client:
            # create dialogs
            for dialog in self._dialogs:
                response = client.post(
                    f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
                    json=dialog["body"],
                )
            # record consent true for first dialog
            dialog = self._dialogs[0]
            response = client.post(
                f"{self._consent_path_prefix}/{dialog['dialog_id']}",
                data="true",
            )
            # check if consent is set for first dialog
            self.assertEqual(response.status_code, 200)
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
            )
            self.assertTrue(json.loads(response.content)["consent_received"])
            # record consent false for first dialog
            response = client.post(
                f"{self._consent_path_prefix}/{dialog['dialog_id']}",
                data="false",
            )
            self.assertEqual(response.status_code, 200)
            # check if first dialog is removed
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
            )
            self.assertEqual(response.status_code, 404)
            # record consent false for second dialog
            dialog = self._dialogs[1]
            response = client.post(
                f"{self._consent_path_prefix}/{dialog['dialog_id']}",
                data="false",
            )
            self.assertEqual(response.status_code, 200)
            # check if second dialog is removed
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
            )
            self.assertEqual(response.status_code, 404)
