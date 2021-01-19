import logging
import os
import timeit
import unittest

import pandas as pd
import yaml
from mimesis.enums import Gender
from mimesis.schema import Field, Schema
from odoo.tests.common import TransactionCase
from odoo.tools.config import config
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

_logger = logging.getLogger(__name__)

_data_path = os.path.join(config.get('data_dir'), 'test_data.csv')

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

        self.cc = self.env['res.config.settings'].create({
            'google_drive_client_id': '321350850398-ub1vd55bmrjmh2oh96oosi0hn1cliufh.apps.googleusercontent.com',
            'google_drive_client_secret': '0jRNrUmCGlZaJQoTSicZ0OcA'
        })
        
        self.cc.set_values()

        self.gdrive = self.env['odoo_file_export.google_drive'].create({
            'name': 'Prueba',
            'file': _data_path,
            #'target_folder_id': "1JU6WrdUUfJR66x3Ct4mgn0ReUWRGDDDd",
            'target_file_name': "pruebatestoddogoogledrive"
        })


    def off_test_upload_to_gdrive(self):
        
                
        gauth = GoogleAuth(settings_file=self.cc.gdrive_settings_file_name())
        d = GoogleDrive(gauth)

        #previamente borramos los ficheros para que no haya un falso positivo
        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and trashed=false"}).GetList()
        for f in files: f.Delete()

        _logger.debug("TEST: Subir fichero al raiz sin borrado local y sobreescribir destino")
        self.gdrive.upload(remove_local_data_file=False)
        assert os.path.exists(self.gdrive.file), \
            "Upload deberia haber respetado el fichero de datos local, no lo ha encontrado"
        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and 'root' in parents and trashed=false"}).GetList()

        assert len(files) == 1, \
            "No coinciden los ficheros subidos. E(1) R({})".format(len(files))
        _logger.debug("TEST: comoprobamos que sobreescribe el destrino")
        self.gdrive.upload(remove_local_data_file=False)
        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and 'root' in parents and trashed=false"}).GetList()

        assert len(files) == 1, \
            "No coincide los ficheros en gdrive despues de dos upload con overwrite=true. E(1) R({})".format(
                len(files)
            )
        _logger.debug("TEST: subir fichero al raiz sin borrado local y sin sobreescribir destino")
        self.gdrive.upload(remove_local_data_file=False, overwrite=False)
        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and 'root' in parents and trashed=false"}).GetList()

        assert len(files) == 2, \
            "No coincide los ficheros gdrive. E(2) R({}). Found:{}".format(
                len(files),
                [(x['id'], x['title']) for x  in files]
            )

        _logger.debug("TEST: subir fichero a carpeta no rai<")
        folder = d.CreateFile({'title': 'pruebatestoddogoogledrive_folder','mimeType' : 'application/vnd.google-apps.folder'})
        folder.Upload()
        self.gdrive.target_folder_id = folder['id']
        self.gdrive.upload(remove_local_data_file=False)

        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and '{}' in parents and trashed=false".format(folder['id'])}).GetList()
        assert 1 == len(files), "No ha creado bien el fichero en el directorio. E(1). R({})".format(len(files))

        _logger.debug("TEST: subir fichero a carpeta no raiz sin sobrescribir destrino y sin borrado local")
        self.gdrive.upload(remove_local_data_file=False, overwrite=False)
        files = d.ListFile({'q': "title = 'pruebatestoddogoogledrive' and '{}' in parents and trashed=false".format(folder['id'])}).GetList()
        assert 2 == len(files), "No ha creado bien el fichero en el directorio. E(2). R({})".format(len(files))

        _logger.debug("TEST: borrado local")
        self.gdrive.upload()
        assert not os.path.exists(_data_path), "No ha borrado el fichero de origen"




