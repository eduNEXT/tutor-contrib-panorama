# Change log

## Version 0.4.0 (2023-04-10)
- Add completion_blockcompletion table

## Version 0.3.1 (2023-02-15)
- Fix bug in push hooks that prevented panorama-elt-logs image to be pushed.

## Version 0.3.0 (2023-01-12)
- Added two settings to control when fluentbit uploads log files: PANORAMA_LOGS_TOTAL_FILE_SIZE (default 1M) and 
PANORAMA_LOGS_UPLOAD_TIMEOUT (default 15m). A new file will be uploaded when it exceeds the total file size,
or after the upload timeout, whatever happens first. Increase these values to reduce traffic (and cost)
when uploading to the datalake. Reduce them to have faster updates.

## 0.2.4
- Improved init command in K8s
- Added PANORAMA_DEBUG option (default=False) to have debug logs
- Added PANORAMA_RUN_K8S_FLUENTBIT option (default=True) to skip fluentbit manifests in K8s

## 0.2.1
- Add the option PANORAMA_USE_SPLIT_MONGO (default True)
## 0.1.9
- Fix: use PANORAMA_REGION in fluentbit configuration
- Improve fluentbit config
- Add student anonymous user id table
- Add site configuration table
- Add PANORAMA_FLB_LOG_LEVEL to set fluent-bit logging level (default: info). 
Set to 'debug' to debug fluentbit.
- Use the aws credentials configured for Panorama, for fluentbit
## 0.1.8
- Fixed a bug in panorama-elt
## 0.1.7
- Enable image building. 
- Create datalake tables and views in the init routine
- Improve readme.
## 0.0.1
- Initial release
