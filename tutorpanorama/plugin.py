from glob import glob
import os
import pkg_resources

from .__about__ import __version__

################# Configuration
config = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "CRONTAB": "55 * * * *",
        "BUCKET": "aulasneo-panorama",
        "RAW_LOGS_BUCKET": "{{ BUCKET }}",
        "BASE_PREFIX": "openedx",
        "REGION": "us-east-1",
        "DATALAKE_DATABASE": "panorama",
        "DATALAKE_WORKGROUP": "panorama",
        "AWS_ACCESS_KEY": "{{ OPENEDX_AWS_ACCESS_KEY }}",
        "AWS_SECRET_ACCESS_KEY": "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}",
        "FLB_LOG_LEVEL": 'info',
        "RUN_K8S_FLUENTBIT": True,
        "DEBUG": False,
        "LOGS_TOTAL_FILE_SIZE": "1M",
        "LOGS_UPLOAD_TIMEOUT": "15m",
        "DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}aulasneo/panorama-elt:{{ PANORAMA_VERSION }}",
        "LOGS_DOCKER_IMAGE": "{{ DOCKER_REGISTRY }}aulasneo/panorama-elt-logs:{{ PANORAMA_VERSION }}",
    },
    # Add here settings that don't have a reasonable default for all users. For
    # instance: passwords, secret keys, etc.
    "unique": {
        # "SECRET_KEY": "\{\{ 24|random_string \}\}",
    },
    # Danger zone! Add here values to override settings from Tutor core or other plugins.
    "overrides": {
        # "PLATFORM_NAME": "My platform",
    },
}

hooks = {
    "init": ["panorama"],
    "build-image": {
        "panorama-elt": "{{ PANORAMA_DOCKER_IMAGE }}",
        "panorama-elt-logs": "{{ PANORAMA_LOGS_DOCKER_IMAGE }}"
    },
    "remote-image": {
        "panorama-elt": "{{ PANORAMA_DOCKER_IMAGE }}",
        "panorama-elt-logs": "{{ PANORAMA_LOGS_DOCKER_IMAGE }}"
    },
}

# Plugin templates

import os
templates = os.path.join(os.path.abspath(os.path.dirname(__file__)), "templates")

# Load all patches from the "patches" folder
patches = {}
for path in glob(
        os.path.join(
            pkg_resources.resource_filename("tutorpanorama", "patches"),
            "*",
        )
):
    with open(path, encoding="utf-8") as patch_file:
        patches.update({os.path.basename(path): patch_file.read()})
