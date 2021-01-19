import logging
import os
import unittest

import pandas as pd
from azure.core.exceptions import ResourceNotFoundError
from azure.core.exceptions import ResourceExistsError

from azure.storage.blob import BlobClient
from mimesis.enums import Gender
from mimesis.schema import Field, Schema
from odoo.tests.common import TransactionCase
from odoo.tools.config import config

_logger = logging.getLogger(__name__)

_data_path = os.path.join(config.get('data_dir'), 'test_blob_data.csv')

class TestGoogleDriveUpload(TransactionCase):

    def setUp(self):
        super(TestGoogleDriveUpload, self).setUp()

        _ = Field('en')
        schema_desc = (
            lambda: {
                'name': _('person.name'),
                'street': _('street_name'),
                'city': _('city'),
                'email': _('person.email'),
                'zip': _('zip_code'),
                'region': _('region'),
                'state': _('state'),
                'date_time': _('formatted_datetime'),
                'company_name': _('company')

            })
        schema = Schema(schema=schema_desc)
        result = schema.create(iterations=1000)     
        pd.DataFrame.from_dict(result).to_csv(_data_path)

        self.blob = self.env['odoo_file_export.blob'].create({
            'name': 'Prueba',
            'file': _data_path,
            'storage_account_url': 'https://pruebasdigitalhigh.blob.core.windows.net/',
            'container': 'octupuscontainer',
            'blob_name': 'test_blob_odoo',
            'credential': 'xwbdS/I9ZYt062FyP8dNIKU8Fac7otp5URvVlhJo/8vGEVEGU6O+N03Bjiu6Y+np85Qe0QPU2b5xkiY9NcJePA=='
        })

    def test_upload(self):

        blob = BlobClient(
            account_url=self.blob.storage_account_url,
            container_name=self.blob.container,
            blob_name=self.blob.blob_name,
            credential=self.blob.credential)

        try:
            blob.get_blob_properties()
            blob.delete_blob()
        except ResourceNotFoundError:
            pass

        _logger.debug("TEST: Subir fichero sin borrar el local")
        self.blob.upload(remove_local_data_file=False)
        assert os.path.exists(_data_path), "Ha borrado el fichero local tras la subida a Blob Storage"
        
        _logger.debug("TEST: Subir fichero que ya esta subido y se sobreescribe sin problemas y no se borra la copia local")
        try:
            self.blob.upload(remove_local_data_file=False)
        except ResourceExistsError:
            self.fail("Ha dado un error de blob existente, cuando deberia haberlo sobreescrito")

        assert os.path.exists(_data_path), "Ha borrado el fichero local tras la subida a Blob storage"

        _logger.debug("TEST: Se sube un fichero sobreescribiendo y borrando la copia local")
        self.blob.upload()
        assert not os.path.exists(_data_path)


        



