import os
import unittest

import yaml
from odoo.tests.common import TransactionCase
from odoo.tools.config import config
#from odoo.addons.extract.models import res_config_settings


class TestResConfigSettings(TransactionCase):
    def setUp(self):
        super(TestResConfigSettings, self).setUp()
        self.config = self.env['res.config.settings'].with_user(self.env.user.id)

    def test_config_save_in_file(self):
        cc = self.config.create({
            'google_drive_client_id': 'client_id_testing',
            'google_drive_client_secret': 'client_secret_testing'
        })

        cc.set_values()
        assert os.path.isfile(cc.gdrive_settings_file_name())

        with open(cc.gdrive_settings_file_name(), 'r') as reader:
            data = yaml.load(reader, Loader=yaml.FullLoader)
            assert 'client_id_testing' == data['client_config']['client_id']
            assert 'client_secret_testing' == data['client_config']['client_secret']

            self.assertIn('https://www.googleapis.com/auth/drive', data['oauth_scope'])
            self.assertIn('https://www.googleapis.com/auth/drive.install', data['oauth_scope'])

            assert data['save_credentials']
            assert 'file' == data['save_credentials_backend']
            credentials_file = os.path.join(config.get('data_dir'), "{}.json".format(cc.gdrive_settings_file_name()))
            assert credentials_file == data['save_credentials_file']

    def test_config_read_from_file(self):
        cc = self.config.create({
            'google_drive_client_id': 'client_id_testing_reading',
            'google_drive_client_secret': 'client_secret_testing_reading'
        })
        cc.set_values()

        values = cc.get_values()
        assert 'client_id_testing_reading' ==  values['google_drive_client_id']
        assert 'client_secret_testing_reading' == values['google_drive_client_secret']
        """
        assert values['save_credentials']
        assert 'file' == 'save_credentials_backend'
        credentials_file = os.path.join(config.get('data_dir'), "{}.json".format(cc.gdrive_settings_file_name()))
        assert credentials_file == values['save_credentials_file']
        """
        
