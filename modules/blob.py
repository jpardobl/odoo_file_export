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
    credential = fields.Char(requried=True)

    def _do_upload(self, blob):
        with open(self.file, "rb") as data:
            blob.upload_blob(data)
        _logger.info("Local file {} uploaded to Blob Storage: {}".format(self.file, self.blob_name))

    def upload(self, remove_local_data_file=True, overwrite=True):

        blob = BlobClient(
            account_url=self.storage_account_url,
            container_name=self.container,
            blob_name=self.blob_name,
            credential=self.credential)

        try:
            self._do_upload(blob)
        except ResourceExistsError as ex:
            if not overwrite: 
                raise ex
            _logger.debug("El fichero existe, hay que sobreescribirlo")
            blob.delete_blob()
            _logger.debug("El fichero se ha borrado para sobreescribirlo")
            self._do_upload(blob)

        if remove_local_data_file: os.unlink(self.file)
