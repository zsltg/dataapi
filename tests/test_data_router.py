# pylint: disable=C0114,C0115,C0116

from fastapi import testclient

from dataapi import main
from tests import test_base


class RoutersDataTest(test_base.BaseTest):
    def test_fetch_on_demand_dialogs(self):
        with testclient.TestClient(main.app) as client:
            # fetch all dialogs, should succeed, return only consented documents
            response = client.get(
                f"{self._data_path_prefix}/",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["total"], self._bulk_consent_count)
            self._create_dialogs_with_one_consent(client)
            # fetch all dialogs, should succeed, return one more dialog
            response = client.get(
                f"{self._data_path_prefix}/",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["total"], self._bulk_consent_count + 1)
            # record consent for all new dialogs
            for dialog in self._on_demand_dialogs:
                response = client.post(
                    f"{self._consent_path_prefix}/{dialog['_id']}",
                    data="true",
                )
            # fetch all dialogs, should succeed, return all new dialogs
            response = client.get(
                f"{self._data_path_prefix}/",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["total"],
                self._bulk_consent_count + len(self._on_demand_dialogs),
            )
            # remove a dialog
            dialog = self._on_demand_dialogs[0]
            client.delete(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}"
            )
            # fetch all dialogs, should succeed, return one less dialogs
            response = client.get(
                f"{self._data_path_prefix}/",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json()["total"],
                self._bulk_consent_count + len(self._on_demand_dialogs) - 1,
            )

    def test_create_dialog(self):
        with testclient.TestClient(main.app) as client:
            # create first dialog, should succeed
            dialog = self._on_demand_dialogs[0]
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
                json=self._get_dialog_request_body(dialog),
            )
            self.assertEqual(response.status_code, 201)
            # create second dialog with same id, should fail
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
                json=self._get_dialog_request_body(dialog),
            )
            self.assertEqual(response.status_code, 409)
            # create third dialog with new id, should succeed
            dialog = self._on_demand_dialogs[1]
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['_id']}",
                json=self._get_dialog_request_body(dialog),
            )
            self.assertEqual(response.status_code, 201)
