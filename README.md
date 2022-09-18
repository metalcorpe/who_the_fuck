# Who The Fuck

## TL;DR

I have spent too much time creating the help me sto there you go...

``` python
usage: who.py [-h] [--skip-blocklist-download] (--service | --cli) (--log-analytics | --csv) [--source-workspace-id SOURCE_WORKSPACE_ID] [--log-analutics-kusto LOG_ANALUTICS_KUSTO]
              [--log-analutics-timedelta LOG_ANALUTICS_TIMEDELTA] [--csv-path CSV_PATH] (--write-log-analytics | --write-csv | --write-blob-storage) [--dest-workspace-id DEST_WORKSPACE_ID]
              [--dest-workspace-shared-key DEST_WORKSPACE_SHARED_KEY] [--csv-dest-folder CSV_DEST_FOLDER] (--storage-account-user-auth | --storage-account-service-auth)
              [--storage-account-name STORAGE_ACCOUNT_NAME] [--storage-account-container-name STORAGE_ACCOUNT_CONTAINER_NAME] [--storage-account-url STORAGE_ACCOUNT_URL]
              [--storage-account-key STORAGE_ACCOUNT_KEY] [--iplist-update-interval IPLIST_UPDATE_INTERVAL] [--ip-analysis-interval IP_ANALYSIS_INTERVAL]

A foo that bars

optional arguments:
  -h, --help            show this help message and exit
  --skip-blocklist-download
  --service
  --cli

IP Source:
  --log-analytics
  --csv
  --source-workspace-id SOURCE_WORKSPACE_ID
                        Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000)
  --log-analutics-kusto LOG_ANALUTICS_KUSTO
                        Kusto query that returns IP list (e.g. Edge_CL | project clientIP | distinct clientIP)
  --log-analutics-timedelta LOG_ANALUTICS_TIMEDELTA
                        Timedelta to search from present in minutes (M) (default 60 minutes)
  --csv-path CSV_PATH

Result Destination:
  --write-log-analytics
  --write-csv
  --write-blob-storage
  --dest-workspace-id DEST_WORKSPACE_ID
                        Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000)
  --dest-workspace-shared-key DEST_WORKSPACE_SHARED_KEY
                        WARNING TEST ONLY. Log Analytics Workspace primary or secondary Connected Sources client authentication key (e.g.
                        WW91IGJldHRlciBub3QgdXNlIHRoZSBzaGFyZWQga2V5IHlvdSBzb24gb2YgYSBiaXRjaCEhIQ==)
  --csv-dest-folder CSV_DEST_FOLDER
                        NOT IMPLEMENTED
  --storage-account-user-auth
                        Enables user authentication using managed identity or az login. Mutually exlusive
  --storage-account-service-auth
                        Enables service authentication using storage account key. Mutually exlusive
  --storage-account-name STORAGE_ACCOUNT_NAME
  --storage-account-container-name STORAGE_ACCOUNT_CONTAINER_NAME
  --storage-account-url STORAGE_ACCOUNT_URL
                        Storage Account URL
  --storage-account-key STORAGE_ACCOUNT_KEY
                        Storage Account Key. Use with --storage-account-service-auth

Service:
  --iplist-update-interval IPLIST_UPDATE_INTERVAL
                        IP List update interval in Hours(H)
  --ip-analysis-interval IP_ANALYSIS_INTERVAL
                        IP List update interval in Seconds (S)

And that's how you'd foo a bar
```
