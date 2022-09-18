# Who The Fuck (Made That Request?)

## Intro

It is a short utility to quickly analyze requesting IPs from deferent sources like Azure Log Anaytics, CSV files, flat log etc. For the time being only Log Analytics Workspace is implemented as a log source. The utility exports logs to Log Analytics and Blob Storage (more options can be inplemented) for corelations.

## TL;DR

I have spent too much time creating the help me sto there you go...

``` bash
usage: who.py [-h] [--skip-blocklist-download] (--service | --cli) (--log-analytics | --csv) --source-workspace-id SOURCE_WORKSPACE_ID --log-analutics-kusto LOG_ANALUTICS_KUSTO
              [--log-analutics-timedelta LOG_ANALUTICS_TIMEDELTA] [--csv-path CSV_PATH] (--write-log-analytics | --write-csv | --write-blob-storage) --dest-workspace-id DEST_WORKSPACE_ID
              --dest-workspace-shared-key DEST_WORKSPACE_SHARED_KEY [--csv-dest-folder CSV_DEST_FOLDER] (--storage-account-user-auth | --storage-account-service-auth)
              --storage-account-container-name STORAGE_ACCOUNT_CONTAINER_NAME --storage-account-url STORAGE_ACCOUNT_URL --storage-account-key STORAGE_ACCOUNT_KEY
              [--iplist-update-interval IPLIST_UPDATE_INTERVAL] [--ip-analysis-interval IP_ANALYSIS_INTERVAL]

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
                        Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000). (env=SOURCEWORKSPACEID)
  --log-analutics-kusto LOG_ANALUTICS_KUSTO
                        Kusto query that returns IP list (e.g. Edge_CL | project clientIP | distinct clientIP). (env=LOGANALYTICSKUSTO)
  --log-analutics-timedelta LOG_ANALUTICS_TIMEDELTA
                        Timedelta to search from present in minutes (M) (default 60 minutes). (env=LOGANALYTICSTIMEDELTA)
  --csv-path CSV_PATH

Result Destination:
  --write-log-analytics
  --write-csv
  --write-blob-storage
  --dest-workspace-id DEST_WORKSPACE_ID
                        Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000). (env=DESTWORKSPACEID)
  --dest-workspace-shared-key DEST_WORKSPACE_SHARED_KEY
                        WARNING TEST ONLY. Log Analytics Workspace primary or secondary Connected Sources client authentication key (e.g.
                        WW91IGJldHRlciBub3QgdXNlIHRoZSBzaGFyZWQga2V5IHlvdSBzb24gb2YgYSBiaXRjaCEhIQ==). (env=DESTWORKSPACESHAREDKEY)
  --csv-dest-folder CSV_DEST_FOLDER
                        NOT IMPLEMENTED
  --storage-account-user-auth
                        Enables user authentication using: ManagedIdentityCredential, SharedTokenCacheCredential, VisualStudioCodeCredential, AzureCliCredential, AzurePowerShellCredential.
                        Mutually exlusive
  --storage-account-service-auth
                        Enables service authentication using storage account key. Mutually exlusive
  --storage-account-container-name STORAGE_ACCOUNT_CONTAINER_NAME
                        (env=STORAGEACCOUNTCONTAINERNAME)
  --storage-account-url STORAGE_ACCOUNT_URL
                        Storage Account URL. (env=STORAGEACCOUNTURL)
  --storage-account-key STORAGE_ACCOUNT_KEY
                        Storage Account Key. Use with --storage-account-service-auth. (env=STORAGEACCOUNTKEY)

Service:
  --iplist-update-interval IPLIST_UPDATE_INTERVAL
                        IP List update interval in Hours(H). (env=IPLISTUPDATEINTERVAL)
  --ip-analysis-interval IP_ANALYSIS_INTERVAL
                        IP List update interval in Seconds (S). (env=IPANALYSISINTERVAL)

And that's how you'd foo a bar
```

## Example

### Example No.1

Collect IPs from log analytics workspace and submit them to another log analytics workspace

``` bash
who.py --service --log-analytics --log-analutics-timedelta=2880 --write-log-analytics --source-workspace-id="00000000-0000-0000-0000-000000000000" --log-analutics-kusto="IPName_CL | project cliIP_s | distinct cliIP_s" --dest-workspace-id="00000000-0000-0000-0000-000000000000" --dest-workspace-shared-key="WW91IGJldHRlciBub3QgdXNlIHRoZSBzaGFyZWQga2V5IHlvdSBzb24gb2YgYSBiaXRjaCEhIQ==" 
```
