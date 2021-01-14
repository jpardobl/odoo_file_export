# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os

import yaml
from odoo import _, api, fields, models
from odoo.tools.config import config

_SETTINGS_FILE_TEMPLATE = """client_config_backend: settings
client_config:
    client_id: {}
    client_secret: {}

save_credentials: True
save_credentials_backend: file
save_credentials_file: {}.json

get_refresh_token: True

oauth_scope:
    - https://www.googleapis.com/auth/drive
    - https://www.googleapis.com/auth/drive.install
"""

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _name = 'res.config.settings'

    google_drive_client_id = fields.Char(string='Client ID',help='OAuth 2.0 Client ID')
    google_drive_client_secret = fields.Char(string='Client Secret', help="OAuth 2.0c Client Secret")

    def gdrive_settings_file_name(self):
        return os.path.join(
            config.get('data_dir'),
            "settings-{}.yaml".format(self.env.user.id)
        )

    def set_values(self):
        _logger.info("Entrando en set_values()")
        super(ResConfigSettings, self).set_values()
    
        fcontents = _SETTINGS_FILE_TEMPLATE.format(
            self.google_drive_client_id,
            self.google_drive_client_secret,
            self.gdrive_settings_file_name()
        )
        #_logger.info(fcontents)
        with open(self.gdrive_settings_file_name(), 'w') as writer:
            writer.write(fcontents)
            _logger.debug("Writing gdrive settings to file: {}".format(
                self.gdrive_settings_file_name()
            ))

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        try:
            with open(self.gdrive_settings_file_name(), 'r') as reader:
                data = yaml.load(reader, Loader=yaml.FullLoader)
                res.update({
                    'google_drive_client_id': data['client_config']['client_id'],
                    'google_drive_client_secret': data['client_config']['client_secret'],
                })
        except Exception as ex:
            _logger.error("Error while reading gdrive settings from file({}): ".format(
                self.gdrive_settings_file_name(),
                ex
            ))
        return res

