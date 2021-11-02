# pylint: disable=C0114,C0115,C0116

from fastapi import testclient

from dataapi import main
from tests import test_base


class RoutersDataTest(test_base.BaseTest):
    def test_create_dialog(self):
        with testclient.TestClient(main.app) as client:
            # create first dialog, should succeed
            dialog = self._dialogs[0]
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 201)
            # create second dialog with same id, should fail
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 409)
            # create third dialog with new id, should succeed
            dialog = self._dialogs[1]
            response = client.post(
                f"{self._data_path_prefix}/{dialog['customer_id']}/{dialog['dialog_id']}",
                json=dialog["body"],
            )
            self.assertEqual(response.status_code, 201)
