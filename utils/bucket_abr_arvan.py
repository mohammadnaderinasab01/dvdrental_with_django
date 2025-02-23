from urllib.parse import quote_plus as urlquote
import boto3
from django.conf import settings
import requests



# elk_base_url = 'elasticsearch://{user_name}:{password}@{host_ip}:{host_port}'
# ELASTIC_SEARCH_URL = elk_base_url.format(user_name='elastic',
# password=urlquote('Fe7$Col9%Da0%Ner9%Mok1$Zat4@H5@Mu0$Z5%Mec9#Do6%Si6#H9$N0@G6#Z6#Go1$Tyt4$D7$Laz9'),
# # password may contain special characters
# host_ip='94.101.189.128',
# host_port=9200)



# AWS_LOCAL_STORAGE = f'{BASE_DIR}/aws/'
AWS_LOCAL_STORAGE_USERS = './users'
AWS_LOCAL_STORAGE_CREATED_SHIRTS = './created_shirts'


class UsersBucket:
    def __init__(self):
        print("users bucket init... ")
        try:
            self.s3_client = boto3.client(
                settings.AWS_SERVICE_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as exc:
            print(exc)

    def DownloadFile(self, src_file_path, dest_file_name):

        object_name =f'{AWS_LOCAL_STORAGE_USERS}{dest_file_name}'

        file = requests.get(src_file_path, allow_redirects=True)

        self.s3_client.put_object(
                ACL='public-read',
                Body=file.content,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def UploadFile(self, src_file_path, filename):
        object_name =f'users/{filename}'
        self.s3_client.put_object(
                ACL='private',
                Body=src_file_path,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def GetDownloadLink(self, filename, ex_in = 3600):
        object_name =f'users/{filename}'
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': object_name
                },
                ExpiresIn=ex_in
            )
            return response
        except:
            print("error")
            return None

    def deleteFile(self, file_name):
        try:
            self.s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=f'users/{file_name}'
            )
        except Exception as e:
            print(e)


class CreatedShirtsBucket:
    def __init__(self):
        print("created_shirts bucket init... ")
        try:
            self.s3_client = boto3.client(
                settings.AWS_SERVICE_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as exc:
            print(exc)

    def DownloadFile(self, src_file_path, dest_file_name):

        object_name =f'{AWS_LOCAL_STORAGE_CREATED_SHIRTS}{dest_file_name}'

        file = requests.get(src_file_path, allow_redirects=True)

        self.s3_client.put_object(
                ACL='public-read',
                Body=file.content,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def UploadFile(self, src_file_path, filename):
        object_name =f'created_shirts/{filename}'
        self.s3_client.put_object(
                ACL='private',
                Body=src_file_path,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=object_name
        )


    def GetDownloadLink(self, filename, ex_in = 3600):
        object_name =f'created_shirts/{filename}'
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': object_name
                },
                ExpiresIn=ex_in
            )
            return response
        except:
            print("error")
            return None


    def deleteFile(self, file_name):
        try:
            self.s3_client.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=f'created_shirts/{file_name}'
            )
        except Exception as e:
            print(e)