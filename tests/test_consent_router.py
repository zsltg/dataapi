# pylint: disable=C0114,C0115,C0116
import json
from fastapi import testclient

from dataapi import main
from tests import test_base


class RoutersDataTest(test_base.BaseTest):
    def test_record_consent(self):
        with testclient.TestClient(main.app) as client:
            response = self._create_dialogs_with_one_consent(client)
            # check if consent is set for first dialog
            dialog = self._on_demand_dialogs[0]
            self.assertEqual(response.status_code, 200)
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
            )
            self.assertTrue(json.loads(response.content)["consent_received"])
            # record consent false for first dialog
            response = client.post(
                f"{self._consent_path_prefix}/{dialog['_id']}",
                data="false",
            )
            self.assertEqual(response.status_code, 200)
            # check if first dialog is removed
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
            )
            self.assertEqual(response.status_code, 404)
            # record consent false for second dialog
            dialog = self._on_demand_dialogs[1]
            response = client.post(
                f"{self._consent_path_prefix}/{dialog['_id']}",
                data="false",
            )
            self.assertEqual(response.status_code, 200)
            # check if second dialog is removed
            response = client.get(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
            )
            self.assertEqual(response.status_code, 404)
