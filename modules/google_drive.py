import logging
import os
import re

import pandas as pd
from odoo import api, fields, models
from odoo.tools.config import config
from odoo.tools.safe_eval import safe_eval
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError, FileNotUploadedError

from google.cloud import storage

_logger = logging.getLogger(__name__)


#TODO post messages to the screen
#TODO add credentials tool to the module

class GoogleDriveUpload(models.Model):
    _name = 'odoo_file_export.google_drive'
    _description = 'Google Drive File Upload'

    name = fields.Char(required=True)
    file = fields.Char(required=True)
    file_mime_type = fields.Char(required=True, default='text/csv')
    target_folder_id = fields.Char(required=False)
    target_file_name = fields.Char(required=True)
    convet_to_google_format = fields.Boolean(default=True)
    google_drive_file_id = fields.Char()

    def _delete_gdrive_file(self, gdrive, file_id):
        try:
            _logger.debug("Trying to delete gdrive file: {}".format(file_id))
            gdrive.CreateFile({'id': file_id}).Delete()
            _logger.debug("File deleted")
        except ApiRequestError as aex:
            _logger.error("Error while deleting gdrive file: {}".format(aex))
        except FileNotUploadedError:
            pass

    def upload(self, overwrite=True, remove_local_data_file=True):
        settings_file = self.env['res.config.settings'].browse().gdrive_settings_file_name()
        _logger.debug("Reading gdrive settings: {}".format(settings_file))
        gauth = GoogleAuth(settings_file=settings_file)
        gdrive_client = GoogleDrive(gauth)

        for record in self:
            try:
                if not os.path.exists(record.file):
                    _logger.error("Cannot find extract file ({}), thus not uploading".format(record.file))
                    continue
                if overwrite and record.google_drive_file_id:
                    record._delete_gdrive_file(gdrive_client, record.google_drive_file_id)
                
                params = {
                    'title': record.target_file_name, 
                    'mimeType': record.file_mime_type,
                    
                }
                if not self.target_folder_id is False:
                    params['parents'] = [{'id': record.target_folder_id}]

                _logger.debug("Uploading file to Google Drive with params: {}".format(params))
                f = gdrive_client.CreateFile(params)
                f.SetContentFile(record.file)
                f.Upload(param={
                    'convert': record.convet_to_google_format
                })
                self.google_drive_file_id = f['id']
                _logger.info("Uploaded extract: {}".format(record.file))

                if remove_local_data_file: os.unlink(record.file)

            except Exception as ex:
                _logger.error("Error uploading extract to gdrive: {}".format(ex))            
                continue
            

