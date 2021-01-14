import logging
import os
import timeit
import unittest

import pandas as pd
import yaml
from mimesis.enums import Gender
from mimesis.schema import Field, Schema
from odoo.addons.extract.models import res_config_settings
from odoo.tests.common import TransactionCase
from odoo.tools.config import config
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

_logger = logging.getLogger(__name__)

_data_path = os.path.join(config.get('data_dir'), 'test_data.csv')

class TestExtract(TransactionCase):

    def setUp(self):
        super(TestExtract, self).setUp()

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
        schema.create(iterations=1000)     
        pd.DataFrame.from_dict(result).to_csv(_data_path)

        cc = self.env['res.config.settings'].create({
            'google_drive_client_id': '321350850398-ub1vd55bmrjmh2oh96oosi0hn1cliufh.apps.googleusercontent.com',
            'google_drive_client_secret': '0jRNrUmCGlZaJQoTSicZ0OcA'
        })
        
        cc.set_values()

        self.gdrive = self.env['odoo_file_export.google_drive'].create({
            'name': 'Prueba',
            'file': _data_path,
            'target_folder_id': "1JU6WrdUUfJR66x3Ct4mgn0ReUWRGDDDd",
            'target_file_name': "prueba"
        })


    def test_upload_to_gdrive(self):
        
                
        gauth = GoogleAuth(settings_file=self.gdrive.settings_file)
        d = GoogleDrive(gauth)


        self.gdrive.upload(remove_local_data_file=False)
        assert os.path.exists(self.extract.full_path()), \
            "Upload deberia haber respetado el fichero de datos local, no lo ha encontrado"
        files = d.ListFile({'q': "title = '{}' and 'root' in parents and trashed=false".format(self.extract.file_name())}).GetList()

        assert len(files) == 1, \
            "No coinciden los ficheros subidos. E(1) R({})".format(len(files))

        self.gdrive.upload(remove_local_data_file=False)
        files = d.ListFile({'q': "title = '{}' and 'root' in parents and trashed=false".format(self.extract.file_name())}).GetList()

        assert len(files) == 1, \
            "No coincide los ficheros en gdrive despues de dos upload con overwrite=true. E(1) R({})".format(
                len(files)
            )

        self.gdrive.upload(overwrite=False)
        files = d.ListFile({'q': "title = '{}' and 'root' in parents and trashed=false".format(self.extract.file_name())}).GetList()

        assert len(files) == 2, \
            "No coincide los ficheros gdrive. E(2) R({}). Found:{}".format(
                len(files),
                [(x['id'], x['title']) for x  in files]
            )


