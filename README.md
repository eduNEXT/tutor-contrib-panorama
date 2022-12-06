# panorama plugin for Tutor

## Introduction

[Panorama](https://www.aulasneo.com/panorama-analytics/) is the analytics solution developed by [Aulasneo](https://www.aulasneo.com) for Open edX. 
It is a complete stack that includes data extraction, load, transformation, 
visualization and analysis. The data extracted is used to build a datalake that can easily
combine multiple LMS installations and even other sources of data.

This utility is in charge of connecting to the MySQL and MongoDB tables and extracting 
the most relevant tables. Then it uploads the data to the datalake and updates all tables and partition.

## Installation

1. Install as a Tutor plugin:
```shell
pip install git+https://github.com/aulasneo/tutor-contrib-panorama
```
2. Enable the plugin
```shell
tutor plugins enable panorama
```

## Setting up the datalake
The Panorama plugin for Tutor is configured to work with a AWS datalake.

To set up your AWS datalake, you will need to:
- create or use an IAM user or role with permissions to access the S3 buckets, KMS if encrypted, Glue and Athena.
- create one S3 bucket to store the data and another as the Athena queries results location
  - we recommend to use encrypted buckets, and to have strict access policies to them
- create the Panorama database in Athena with `CREATE DATABASE panorama`
- create the Athena workgroup to keep the queries isolated from other projects
  - set the 'Query result location' to the bucket created for this workgroup

### User permissions to work with AWS datalake

In order to work with a AWS datalake, you will need to create a user (e.g. _panorama-elt_)
and assign a policy (named e.g. _PanoramaELT_) with at least the following permissions.

Replace **\<region>** and **\<account id>** with proper values. 

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "glue:BatchCreatePartition",
                "glue:GetDatabase",
                "athena:StartQueryExecution",
                "glue:CreateTable",
                "athena:GetQueryExecution",
                "athena:GetQueryResults",
                "glue:GetDatabases",
                "glue:GetTable",
                "glue:DeleteTable",
                "glue:GetPartitions",
                "glue:UpdateTable"
            ],
            "Resource": [
                "arn:aws:athena:<region>:<account id>:workgroup/panorama",
                "arn:aws:glue:<region>:<account id>:database/panorama",
                "arn:aws:glue:<region>:<account id>:catalog",
                "arn:aws:glue:<region>:<account id>:table/panorama/*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        }
    ]
}
```

If you have encrypted S3 buckets with KMS, you may need to add permissions to get
the KMS keys.

## Configuration

Mandatory variables:

- PANORAMA_BUCKET: S3 bucket to store the data

Optional variables (defaults will generally work):

- PANORAMA_RAW_LOGS_BUCKET: S3 bucket to store the tracking logs (Default: PANORAMA_BUCKET).
- PANORAMA_CRONTAB: Crontab entry to update the datasets. The recommended period is one hour. (Default: "55 * * * *")
- PANORAMA_BASE_PREFIX: Directory inside the PANORAMA_BUCKET to store the raw data (Default "openedx")
- PANORAMA_REGION: AWS default region (Default "us-east-1")
- PANORAMA_DATALAKE_DATABASE: Name of the AWS Athena database (Default "panorama")
- PANORAMA_DATALAKE_WORKGROUP: Name of the AWS Athena workgroup (Default "panorama")
- PANORAMA_AWS_ACCESS_KEY: AWS access key (Default OPENEDX_AWS_ACCESS_KEY)
- PANORAMA_AWS_SECRET_ACCESS_KEY: AWS access secret OPENEDX_AWS_SECRET_ACCESS_KEY)
- PANORAMA_USE_SPLIT_MONGO (default True): Set to false for versions older than Maple

## Datalake directory structure

For each table (or for each field-based partition in each table when enabled), one file in csv format
will be generated and uploaded. The file will have the same name as the table, with '.csv' extension.

Each CSV file will be uploaded to the following directory structure:

```
s3://<bucket>/[<base prefix>/]<table name>/[<base partitions>/][field partitions/]<table name>.csv
```
Where:
- bucket: is the bucket name, configured in the `panorama_raw_data_bucket` setting
- base prefix: (optional) subdirectory to hold tables of a same kind of system. E.g.: openedx. 
It can receive files from multiple sources, as long as the table names are the same and share a field structure 
- table name: base location of the datalake table. All text files inside this directory must have exactly the same column structure
- base partitions: partitions common to a same installation, in Hive format. 
These are not based on fields in the data sources, but will appear as fileds in the datalake.
For multiple Open edX installations, the default is to use 'lms' as field name and the LMS_HOST as the value, which is the LMS url.
E.g.: 'lms=openedx.example.com'
- field partitions: (optional) For large tables, it's possible to split the datasource in multiple csv files.
The field will be removed from the csv file, but will appear as a partition field in the datalake.
In Open edX installations, the default setting is to partition courseware_studentmodule table by course_id.

## License

This software is licenced under Apache 2.0 license. Please see LICENSE for more details.

## Contributing

Contributions are welcome! Please submit your PR and we will check it.
For questions, please send an email to <mailto:andres@aulasneo.com>.

