# -- coding: utf-8 --

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
import time


settings: AppSettings = get_app_settings()

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在CosConfig中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = settings.COS_SECRET_ID     # 替换为用户的 SecretId，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
secret_key = settings.COS_SECRET_KEY   # 替换为用户的 SecretKey，请登录访问管理控制台进行查看和管理，https://console.cloud.tencent.com/cam/capi
region = settings.COS_REGION      # 替换为用户的 region，已创建桶归属的region可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
bucket_name = settings.COS_BUCKET_NAME
                           # COS支持的所有region列表参见https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见https://cloud.tencent.com/document/product/436/14048
scheme = 'https'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)



def upload_file_to_cos(file_name):
    is_success= False
    global client
    for i in range(0, 10):
        time.sleep(1)
        try:
            response = client.upload_file(
                Bucket=bucket_name,
                Key=file_name,
                LocalFilePath='./uploadfile/'+file_name)
            is_success =True
            break
        except CosClientError or CosServiceError as e:
            client = CosS3Client(config)
            logging.error(f"cos上传失败报错：{e}")
    return is_success


def get_read_url(file_name):
    return settings.COS_REQUEST_URL+"/"+file_name