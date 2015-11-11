__author__ = 'dbro'
from django.apps import apps as django_apps
from django.conf import settings
from storage_provisioner.provisioner import S3StorageProvisioner

STORAGE_PROVISIONER = None
STREAM_MODEL = None

BROADCAST_SETTINGS = getattr(settings, "BROADCAST_SETTINGS", None)

if not BROADCAST_SETTINGS or len(BROADCAST_SETTINGS.keys()) != 2:
    print(BROADCAST_SETTINGS)
    raise RuntimeError("settings.BROADCAST_STORAGE_SETTINGS must specify exactly one provider and a 'STREAM_MODEL'")

if "S3" in BROADCAST_SETTINGS.keys():
    s3_params = BROADCAST_SETTINGS["S3"]
    aws_access_key_id = BROADCAST_SETTINGS["S3"]['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = BROADCAST_SETTINGS["S3"]['AWS_SECRET_ACCESS_KEY']
    s3_bucket = BROADCAST_SETTINGS["S3"]['BUCKET']
    STORAGE_PROVISIONER = S3StorageProvisioner(aws_access_key_id,
                                               aws_secret_access_key)

if "STREAM_MODEL" in BROADCAST_SETTINGS.keys():
    STREAM_MODEL = django_apps.get_model(BROADCAST_SETTINGS['STREAM_MODEL'])

if STORAGE_PROVISIONER is None:
    raise RuntimeError("settings.BROADCAST_STORAGE_SETTINGS contained an invalid selection")
