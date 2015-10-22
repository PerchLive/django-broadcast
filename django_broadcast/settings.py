__author__ = 'dbro'

from django.conf import settings
from storage_provisioner.provisioner import S3StorageProvisioner

STORAGE_PROVISIONER = None

BROADCAST_SETTINGS = getattr(settings, "BROADCAST_SETTINGS", None)

if not BROADCAST_SETTINGS or len(BROADCAST_SETTINGS.keys()) != 1:
    raise RuntimeError("settings.BROADCAST_STORAGE_SETTINGS must specify exactly one provider")

# Required parameters for each Storage Provider
SUPPORTED_PROVIDERS = {
    "S3": ["AWS_ACCESS_KEY", "AWS_ACCESS_SECRET"]
}

if BROADCAST_SETTINGS.keys()[0] == "S3":
    s3_params = SUPPORTED_PROVIDERS["S3"]
    STORAGE_PROVISIONER = S3StorageProvisioner(s3_params[0],  # AWS_ACCESS_KEY
                                               s3_params[1])  # AWS_ACCESS_SECRET

if STORAGE_PROVISIONER is None:
    raise RuntimeError("settings.BROADCAST_STORAGE_SETTINGS contained an invalid selection")