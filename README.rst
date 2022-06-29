panorama plugin for `Tutor <https://docs.tutor.overhang.io>`__
===================================================================================

Installation
------------

::

    pip install git+https://github.com/aulasneo/tutor-contrib-panorama

Usage
-----

::

    tutor plugins enable panorama

Note: Currently tracking logs extraction and load is only supported in Kubernetes Tutor deployments
(not in Tutor local installation).

Configuration
-------------

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


License
-------

This software is licensed under the terms of the AGPLv3.