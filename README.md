# Odoo File Export

Odoo Module that uploads files from Odoo server file system to Cloud File Services.

So far it uploads to Azure Blob Storage and Google Drive

## Azure Blob Storage

**Module:** *odoo_file_export.blob*

**Fields:**

- name The name of the job, just choose a name that help you identify the job later in time.
- file The name of the file that is going to be uploaded. This file must be at *data_dir* path (from Odoo configuration).
- storage_account_url The Azure Storage url where the file must be uploaded
- container The of the container where the file must be uploaded.
- blob_name The target name of the file, how is it goiung to be identified once at the cloud.
- credential The Access to the Azure Storage Account.

**Brief

Each uploader that is configured is to upload one file. Thus each file can be uploaded to a different Storage Account or container.

After the uploader uploads the file it unlinks the local file. *next releases will allow the user to decide whether he wants the local file to be downloaded*

The uploader overwrites any posible blob that is already at the container with the same name. *next releases will allow the user to decide whether he wants the blob to be overwriten.*

### Getting started

First you need to create an Azure account which is explained here:

https://docs.microsoft.com/es-es/azure/storage/common/storage-account-create?tabs=azure-portal

Next, you need to enable a Storage Account:

https://docs.microsoft.com/azure/storage/blobs/storage-blob-create-account-block-blob?tabs=azure-portal

**Keep the Storage Account Url, you will need it to configure a blob uploader in Odoo.

Also, you need to create a *container* inside the Storage Account to host the blob. 

**Again please keep the contianer name to use it in the blob uploader configuration**

Last, you just need to create a new Blob Uploader in Odoo. Please refer to the previos field explanation to do this configuration.

Yo can use the *Accion->Upload* in Odoo UI once selected the newly created Blob Uploader to make it work.

Also you can upload by code as follows:

```
selv.env['odoo_file_export.blob'].browse(<id>).upload()
```
or if you have multiple uploaders.
```
selv.env['odoo_file_export.blob'].search([]).upload()
'''
  
### Testing the module

Open the file tests/test_blob.py and fill in the Azure Service access detail.

```
STORAGE_ACCOUNT_URL = 'https://.....'
CONTAINER = '.............'
CREDENTIAL = 'DGFDFGDFG....'
```

Launch the following command from the odoo path
```
>>> odoo-bin -c <odoo_config_file_path> --log-level=debug --test-tags=odoo_file_export -d <testing_database_name>
```




