import argparse
import os
import zipfile
from auth import init_client
from myauto_parser import download_images


def upload_images_from_zip(s3_client, bucket_name, zip_file_path, s3_key_prefix):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                s3_client.upload_fileobj(zip_ref.open(file_name), bucket_name, f'{s3_key_prefix}/{file_name}', ExtraArgs={'ContentType': 'image/jpeg'})
                print(f'Uploaded {file_name}')
def main():
    s3_client = init_client()
    parser = argparse.ArgumentParser(description='Upload images from a downloaded zip file to S3')
    parser.add_argument('-bn', '--bucket_name', help='Name of the S3 bucket')
    parser.add_argument('-zfp', '--zip_file_path', help='Path to the downloaded zip file')
    parser.add_argument('-skp', '--s3_key_prefix', help='Prefix to prepend to S3 object keys')
    parser.add_argument('-pm', '--parse_myauto', help='Parse or not photos from MyAuto', choices=['False', 'True'], type=str, nargs='?', const='False', default='False')
    args = parser.parse_args()


    if args.parse_myauto == 'True':
        download_images()

    bucket_name = args.bucket_name
    zip_file_path = args.zip_file_path
    s3_key_prefix = args.s3_key_prefix

    upload_images_from_zip(s3_client, bucket_name, zip_file_path, s3_key_prefix)


if __name__ == '__main__':
    main()
