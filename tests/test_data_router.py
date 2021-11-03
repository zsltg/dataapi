# pylint: disable=C0114,C0115,C0116

from fastapi import testclient

from dataapi import main
from tests import test_base


class RoutersDataTest(test_base.BaseTest):
    def test_fetch_dialogs_with_params(self):
        with testclient.TestClient(main.app) as client:
            # dialogs in English
            response = client.get(
                f"{self._data_path_prefix}/?language=EN",
            )
            self.assertEqual(self._language_counts[0], response.json()["total"])
            # dialogs in German
            response = client.get(
                f"{self._data_path_prefix}/?language=DE",
            )
            self.assertEqual(self._language_counts[1], response.json()["total"])
            # dialogs in Italian
            response = client.get(
                f"{self._data_path_prefix}/?language=IT",
            )
            self.assertEqual(self._language_counts[2], response.json()["total"])
            # dialogs in French
            response = client.get(
                f"{self._data_path_prefix}/?language=FR",
            )
            self.assertEqual(self._language_counts[3], response.json()["total"])
            # dialogs for a random customer
            response = client.get(
                f"{self._data_path_prefix}/?customer_id={self._a_customer_id}",
            )
            self.assertEqual(
                self._dialog_count_for_a_customer, response.json()["total"]
            )
            # dialogs for a random customer in a language
            response = client.get(
                f"{self._data_path_prefix}/"
                f"?language={self._a_language_for_a_customer}&customer_id={self._a_customer_id}"
            )
            self.assertEqual(
                self._dialog_count_for_a_customer_in_language, response.json()["total"]
            )
            # paginate through the consented dialogs
            item_count = 0
            for i in range(0, 500, 50):
                response = client.get(
                    f"{self._data_path_prefix}/?limit=50&offset={i}",
                )
                item_count += len(response.json()["items"])
            self.assertEqual(self._bulk_consent_count, item_count)

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
