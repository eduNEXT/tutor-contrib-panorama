from __future__ import annotations

from glob import glob
import os
import pkg_resources

from tutor import env, hooks

from .__about__ import __version__

################# Configuration
config = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "CRONTAB": "55 * * * *",
        "BUCKET": "aulasneo-panorama",
        "RAW_LOGS_BUCKET": "{{ PANORAMA_BUCKET }}",
        "BASE_PREFIX": "openedx",
        "REGION": "us-east-1",
        "DATALAKE_DATABASE": "panorama",
        "DATALAKE_WORKGROUP": "panorama",
        "AWS_ACCESS_KEY": "{{ OPENEDX_AWS_ACCESS_KEY }}",
        "AWS_SECRET_ACCESS_KEY": "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}",
        "FLB_LOG_LEVEL": 'info',
        "USE_SPLIT_MONGO": True,
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

################# Initialization tasks
MY_INIT_TASKS: list[tuple[str, tuple[str, ...], int]] = [
    ("panorama", ("panorama", "tasks", "panorama-elt", "init"), hooks.priorities.LOW),
]

# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path, priority in MY_INIT_TASKS:
    full_path: str = pkg_resources.resource_filename(
        "tutorpanorama", os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task), priority=priority)

################# Docker image management
# To build an image with `tutor images build myimage`
hooks.Filters.IMAGES_BUILD.add_item((
    "panorama",
    ("plugins", "panorama", "build", "panorama-elt"),
    "{{ PANORAMA_DOCKER_IMAGE }}",
    (),
))
hooks.Filters.IMAGES_BUILD.add_item((
    "panorama",
    ("plugins", "panorama", "build", "panorama-elt-logs"),
    "{{ PANORAMA_LOGS_DOCKER_IMAGE }}",
    (),
))
# To pull/push an image with `tutor images pull myimage` and `tutor images push myimage`:
hooks.Filters.IMAGES_PULL.add_item((
    "panorama",
    "{{ PANORAMA_DOCKER_IMAGE }}",
))
hooks.Filters.IMAGES_PULL.add_item((
    "panorama",
    "{{ PANORAMA_LOGS_DOCKER_IMAGE }}",
))
hooks.Filters.IMAGES_PUSH.add_item((
    "panorama",
    "{{ PANORAMA_DOCKER_IMAGE }}",
))
hooks.Filters.IMAGES_PUSH.add_item((
    "panorama",
    "{{ PANORAMA_LOGS_DOCKER_IMAGE }}",
))

# TODO: implement logs extraction and load of tracking logs in local installations

################# You don't really have to bother about what's below this line,
################# except maybe for educational purposes :)

# Plugin templates
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("tutorpanorama", "templates")
)
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("panorama/build", "plugins"),
        ("panorama/apps", "plugins"),
    ],
)
# Load all patches from the "patches" folder
for path in glob(
        os.path.join(
            pkg_resources.resource_filename("tutorpanorama", "patches"),
            "*",
        )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

# Load all configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        (f"PANORAMA_{key}", value)
        for key, value in config["defaults"].items()
    ]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        (f"PANORAMA_{key}", value)
        for key, value in config["unique"].items()
    ]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config["overrides"].items()))
