import json
import os

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from libs.la_functions import post_data
from libs.logger import logging

log = logging.getLogger(os.path.basename(__file__))


class LAHandler:
    def __init__(self, workspace_id, shared_key) -> None:
        self.workspace_id = workspace_id
        self.shared_key = shared_key

    def send(self, result, log_type):
        body = json.dumps(result)
        post_data(self.workspace_id, self.shared_key, body, log_type)


class CSVHandler:
    def __init__(self) -> None:
        # TODO: Implement
        raise NotImplementedError

    def send(self, result, log_type):
        # TODO: Implement
        raise NotImplementedError


class BlobHandler:
    def __init__(
        self,
        storage_account_user_auth,
        storage_account_service_auth,
        storage_account_url,
        storage_account_key,
        storage_account_container_name,
    ) -> None:
        self.storage_account_user_auth = storage_account_user_auth
        self.storage_account_service_auth = storage_account_service_auth
        self.storage_account_url = storage_account_url
        self.storage_account_key = storage_account_key
        self.storage_account_container_name = storage_account_container_name

        if self.storage_account_user_auth:
            self.credential = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(
                account_url=self.storage_account_url,
                credential=DefaultAzureCredential(),
            )
        elif self.storage_account_service_auth:
            blob_service_client = BlobServiceClient(
                account_url=self.storage_account_url,
                credential=self.storage_account_key,
            )

        else:
            raise NotImplementedError
        # Instantiate a new ContainerClient
        self.container_client = blob_service_client.get_container_client(
            self.storage_account_container_name
        )

        try:
            # Create new Container in the Service
            self.container_client.create_container()
        except ResourceExistsError as e:
            log.warn(e)

    def append_data_to_blob(self, result, log_type):
        # Instantiate a new BlobClient
        blob_client = self.container_client.get_blob_client(log_type)

        # Upload content to the Page Blob
        for i_result in result:
            i_result_dump = json.dumps(i_result)
            blob_client.upload_blob(i_result_dump + "\n", blob_type="AppendBlob")
            print("Data Appended to Blob Successfully.")

    def send(self, result, log_type):
        self.append_data_to_blob(result, log_type)


class DestinationHandler:
    def __init__(self, args) -> None:
        if args.write_log_analytics:
            self.handler = LAHandler(
                args.dest_workspace_id, args.dest_workspace_shared_key
            )
        elif args.write_csv:
            self.handler = CSVHandler()
            raise NotImplementedError
        elif args.write_blob_storage:
            self.handler = BlobHandler(
                args.storage_account_user_auth,
                args.storage_account_service_auth,
                args.storage_account_url,
                args.storage_account_key,
                args.storage_account_container_name,
            )
        else:
            raise NotImplementedError

    def commit(self, result, log_type):
        self.handler.send(result, log_type)
