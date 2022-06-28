python /panorama-elt/panorama.py --settings=/config/panorama_openedx_settings.yaml --debug test-connections
python /panorama-elt/panorama.py --settings=/config/panorama_openedx_settings.yaml --debug create-datalake-tables --all
python /panorama-elt/panorama.py --settings=/config/panorama_openedx_settings.yaml --debug create-table-views --all