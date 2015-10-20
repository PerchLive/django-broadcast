__author__ = 'dbro'

from models import Stream
from storage_provisioner.provisioner import S3StorageProvisioner


def provision_s3_storage_for_stream(provisioner: S3StorageProvisioner, stream: Stream, aws_policy: str, aws_region: str,
                                    bucket_name: str, bucket_path: str) -> Storage:
    return provisioner.provision_storage(policy=aws_policy, aws_region=aws_region, bucket_name=bucket_name, bucket_path=bucket_path)
