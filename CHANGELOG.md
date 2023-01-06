# Change log
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
