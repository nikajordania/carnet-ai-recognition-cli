# Car Recognition Service

## Service Architecture
![image description](service_architecture.svg)

Upload images from a downloaded zip file to S3


options:
* -bn, --bucket_name BUCKET_NAME (Name of the S3 bucket)

* -zfp, --zip_file_path ZIP_FILE_PATH (Path to the downloaded zip file)

* -skp, --s3_key_prefix S3_KEY_PREFIX (Prefix to prepend to S3 object keys)

* -pm, --parse_myauto [{False,True}] (Parse or not photos from MyAuto)


```bash
python main.py -bn bucket_name -zfp downloaded_images.zip -skp myavto -pm True
```
