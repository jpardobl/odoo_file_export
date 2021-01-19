import logging
import os
import re

import pandas as pd
from odoo import api, fields, models
from odoo.tools.config import config
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobClient

_logger = logging.getLogger(__name__)



class BlobUpload(models.Model):
    _name = 'odoo_file_export.blob'
    _description = 'Blob File Upload'

    name = fields.Char(required=True)
    file = fields.Char(required=True)
    storage_account_url = fields.Char(required=True)
    container = fields.Char(required=True)
    blob_name = fields.Char(required=True)
    credential = fields.Char(required=True)

    def _do_upload(self, blob, file_full_path):
        with open(file_full_path, "rb") as data:
            blob.upload_blob(data)
        _logger.info("Local file {} uploaded to Blob Storage: {}".format(file_full_path, self.blob_name))

    def upload(self, remove_local_data_file=True, overwrite=True):
        for record in self:
            try:
                file_full_path = os.path.join(config.get('data_dir'), record.file)
                if not os.path.exists(file_full_path):
                    _logger.error("Cannot find file ({}), thus not uploading".format(file_full_path))
                    continue

                blob = BlobClient(
                    account_url=record.storage_account_url,
                    container_name=record.container,
                    blob_name=record.blob_name,
                    credential=record.credential)

                try:
                    record._do_upload(blob, file_full_path)
                except ResourceExistsError as ex:
                    if not overwrite: 
                        _logger.info("El fichero existe, no sd sobreescribe por que overwrite=False")
                        continue
                    _logger.debug("El fichero existe, hay que sobreescribirlo")
                    blob.delete_blob()
                    _logger.debug("El fichero se ha borrado para sobreescribirlo")
                    record._do_upload(blob, file_full_path)

                if remove_local_data_file: os.unlink(file_full_path)
            except Exception as ex:
                _logger.error("Error uploading to Blob: type({}), {}".format(type(ex), ex))            
                continue
