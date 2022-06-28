from glob import glob
import os
import pkg_resources

from tutor import hooks

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
        "AWS_SECRET_ACCESS_KEY": "{{ OPENEDX_AWS_SECRET_ACCESS_KEY }}"

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
# To run the script from templates/panorama/tasks/myservice/init, add:
hooks.Filters.COMMANDS_INIT.add_item((
    "panorama",
    ("panorama", "tasks", "panorama-elt", "init.sh"),
))

################# Docker image management
# To build an image with `tutor images build myimage`
hooks.Filters.IMAGES_BUILD.add_item((
    "panorama-elt",
    ("plugins", "panorama", "build", "panorama-elt"),
    "docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}",
    (),
))
hooks.Filters.IMAGES_BUILD.add_item((
    "panorama-elt",
    ("plugins", "panorama", "build", "panorama-elt-logs"),
    "docker.io/aulasneo/panorama-elt-logs:{{ PANORAMA_VERSION }}",
    (),
))
# To pull/push an image with `tutor images pull myimage` and `tutor images push myimage`:
hooks.Filters.IMAGES_PULL.add_item((
    "panorama-elt",
    "docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}",
))
hooks.Filters.IMAGES_PULL.add_item((
    "panorama-elt-logs",
    "docker.io/aulasneo/panorama-elt-logs:{{ PANORAMA_VERSION }}",
))
hooks.Filters.IMAGES_PUSH.add_item((
    "panorama-elt",
    "docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}",
))
hooks.Filters.IMAGES_PUSH.add_item((
    "panorama-elt-logs",
    "docker.io/aulasneo/panorama-elt-logs:{{ PANORAMA_VERSION }}",
))

# Docker image for local installation
hooks.Filters.ENV_PATCHES.add_item(
    (
        "local-docker-compose-services",
        """
panorama:
    image: docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}
    volumes:
        - ../plugins/panorama/apps/panorama-elt/panorama_openedx_settings.yaml:/config/panorama_openedx_settings.yaml:ro
        - ../plugins/panorama/apps/panorama-elt/crontab:/etc/cron.d/crontab:ro
    command: bash -c "crontab /etc/cron.d/crontab && exec cron -f"
    restart: unless-stopped
"""
    )
)

# TODO: implement logs extraction and load of tracking logs in local installations

hooks.Filters.ENV_PATCHES.add_item(
    (
        "local-docker-compose-jobs-services",
        """
panorama-job:
    image: docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}
    volumes:
        - ../plugins/panorama/apps/panorama-elt/panorama_openedx_settings.yaml:/config/panorama_openedx_settings.yaml:ro
""",
    )
)

# Docker image for local dev installation
hooks.Filters.ENV_PATCHES.add_item(
    (
        "local-docker-compose-dev-services",
        """
panorama:
    stdin_open: true
    tty: true
""",
    )
)

# Panorama for K8s

# Panorama ELT deployment

# Init job. Will only run a connection test
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-jobs",
    """
---
apiVersion: batch/v1
kind: Job
metadata:
  name: panorama-job
  labels:
    app.kubernetes.io/name: panorama-elt
spec:
  template:
    metadata:
      labels:
        app.kubernetes.io/name: panorama-elt
    spec:
      restartPolicy: Never
      containers:
        - name: panorama-elt
          image: docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}
          volumeMounts:
            - mountPath: /config/
              name: config
          command:
            - /bin/sh
            - -c
            - python /panorama-elt/panorama.py --settings /config/panorama_openedx_settings.yaml test-connections;python /panorama-elt/panorama.py --settings /config/panorama_openedx_settings.yaml create-datalake-tables --all;python /panorama-elt/panorama.py --settings /config/panorama_openedx_settings.yaml create-table-views --all
      volumes:
        - name: config
          configMap:
            name: panorama-elt-config
"""))

# Cronjob. Will query the db and upload to the datalake periodically
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-jobs",
    """
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: panorama-elt
  labels:
    app.kubernetes.io/name: panorama-elt
spec:
  schedule: {{ PANORAMA_CRONTAB }}
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app.kubernetes.io/name: panorama-elt
        spec:
          restartPolicy: Never
          containers:
            - name: panorama-elt
              image: docker.io/aulasneo/panorama-elt:{{ PANORAMA_VERSION }}
              volumeMounts:
                - mountPath: /config/
                  name: config
              command:
                - /bin/sh
                - -c
                - python /panorama-elt/panorama.py --settings /config/panorama_openedx_settings.yaml extract-and-load --all
          volumes:
            - name: config
              configMap:
                name: panorama-elt-config
"""))

# Config map with the configuration file for panorama-elt
hooks.Filters.ENV_PATCHES.add_item((
    "kustomization-configmapgenerator",
    """
- name: panorama-elt-config
  files:
    - ../env/plugins/panorama/apps/panorama-elt/panorama_openedx_settings.yaml
  options:
    labels:
        app.kubernetes.io/name: panorama-elt
"""))

# Panorama logs (fluentbit) for K8s - ClusterRole
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-deployments",
    """
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-log-reader
rules:
- apiGroups: [""]
  resources:
  - namespaces
  - pods
  verbs: ["get", "list", "watch"]
"""))

# Panorama logs (fluentbit) for K8s - ClusterRoleBinding
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-deployments",
    """
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: pod-log-crb
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: pod-log-reader
subjects:
- kind: ServiceAccount
  name: fluent-bit
  namespace: kube-system
"""))

# Panorama logs (fluentbit) for K8s - ConfigMap
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-deployments",
    """
---
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    app.kubernetes.io/name: fluentbit
  name: fluent-bit-config
  namespace: kube-system
data:
  fluent-bit.conf: |
    [SERVICE]
        Parsers_File  parsers.conf
    [INPUT]
        Name              tail
        Tag               kube.*
        Path              /var/log/containers/lms*.log
        Exclude_Path      /var/log/containers/lms-worker*.log
        Parser            docker
        DB                /var/log/flb_kube.db
        Mem_Buf_Limit     256MB
        DB.locking        true
        Rotate_Wait       30
        Docker_Mode       On
        Docker_Mode_Flush 10
        Skip_Long_Lines   On
        Refresh_Interval  10
    [FILTER]
        Name             kubernetes
        Match            kube.*
        Kube_URL         https://kubernetes.default.svc:443
        Kube_CA_File     /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        Kube_Token_File  /var/run/secrets/kubernetes.io/serviceaccount/token
        Kube_Tag_Prefix  kube.var.log.containers.
        Merge_Log        On
        Merge_Log_Key    log_processed
    [FILTER]
        Name             grep
        Match            *
        Regex            log ^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d INFO \d+ \[tracking\] .*$
    [FILTER]
        Name             parser
        Match            *
        Key_Name         log
        Parser           event
    [OUTPUT]
        Name             s3
        Match            *
        bucket           {{ PANORAMA_RAW_LOGS_BUCKET }}
        region           us-east-1
        compression      gzip
        use_put_object   On
        s3_key_format    /openedx/tracking_logs/$TAG[1]/year=%Y/month=%m/day=%d/tracking.log-%Y%m%d-%H%M%S-$UUID.gz
        s3_key_format_tag_delimiters  _
        total_file_size  30M
        upload_timeout   3m
        log_key          event

  parsers.conf: |
    [PARSER]
        Name             docker
        Format           json
        Time_Key         time
        Time_Format      %Y-%m-%dT%H:%M:%S.%L
        Time_Keep        On
    [PARSER]
        Name              event
        Format            regex
        Regex             ^[^\{]+(?<event>\{.*\})$
    [PARSER]
        Name              tracking-parser
        Format            regex
        Regex             ^(?<timestamp>[^ ] [^ ]) (?<level>.+) \d+ \[(?<logtype>.+)\] \[user (?<user>\d+)\] \[ip (?<ip>[0-9\.]+)\] (?<process>[^ ]+) - (?<eventlog>.*)$
        Time_Key          timestamp
        Time_Format       %Y-%m-%d %H:%M:%S,%L
"""))

# Panorama logs (fluentbit) for K8s - DaemonSet
hooks.Filters.ENV_PATCHES.add_item((
    "k8s-deployments",
    """
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentbit
  namespace: kube-system
  labels:
    app.kubernetes.io/name: fluentbit
spec:
  selector:
    matchLabels:
      name: fluentbit
  template:
    metadata:
      labels:
        name: fluentbit
    spec:
      serviceAccountName: fluent-bit
      containers:
      - name: aws-for-fluent-bit
        image: docker.io/aulasneo/panorama-elt-logs:0.1.4
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluent-bit-config
          mountPath: /fluent-bit/etc/
        - name: mnt
          mountPath: /mnt
          readOnly: true
        resources:
          limits:
            memory: 256Mi
          requests:
            cpu: 500m
            memory: 100Mi
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluent-bit-config
        configMap:
          name: fluent-bit-config
      - name: mnt
        hostPath:
          path: /mnt
    """)
)

# Panorama logs (fluentbit) for K8s - Patch daemon set namespace
# Log extraction is done for all namespaces at a time, and must not be in
# an app namespace, but in kube-system.
# Currently, Kustomization overrides all namespaces in all resources.
# This is a known limitation disussed in this issue: https://github.com/kubernetes-sigs/kustomize/issues/880
# This path allows overriding the namespace of the fluentbit daemonset.
hooks.Filters.ENV_PATCHES.add_item((
    "kustomization",
    """
patchesJson6902:
  - target:
      group: ""
      version: v1
      kind: DaemonSet
      name: fluentbit
    patch: |-
      - op: replace
        path: /metadata/namespace
        value: kube-system
"""))


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
