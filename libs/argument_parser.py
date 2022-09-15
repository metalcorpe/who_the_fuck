
import argparse
import os


parser = argparse.ArgumentParser(prog=os.path.basename(__file__))

parser.add_argument("--skip-blocklist-download",
    dest="skip_blocklist_download",
    action="store_true"
                    )

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--service", action="store_true")
group.add_argument("--cli", action="store_true")

source_group = parser.add_argument_group("IP Source")
source_group2 = source_group.add_mutually_exclusive_group(required=True)
source_group2.add_argument(
    "--log-analytics", dest="log_analytics", action="store_true"
)
source_group2.add_argument("--csv", action="store_true")
source_group.add_argument(
    "--source-workspace-id",
    dest="source_workspace_id",
    type=str,
    help="Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000)",
)
source_group.add_argument(
    "--log-analutics-kusto",
    dest="log_analutics_kusto",
    type=str,
    help="Kusto query that returns IP list (e.g. Edge_CL | project clientIP | distinct clientIP)",
)
source_group.add_argument(
    "--log-analutics-timedelta",
    dest="log_analutics_timedelta",
    type=int,
    default=60,
    help="Timedelta to search from present in minutes (M) (default 60 minutes)",
)
source_group.add_argument("--csv-path", dest="csv_path", type=str)

dest_group = parser.add_argument_group("Result Destination")
dest_group2 = dest_group.add_mutually_exclusive_group(required=True)
dest_group2.add_argument(
    "--write-log-analytics", dest="write_log_analytics", action="store_true"
)
dest_group2.add_argument("--write-csv", dest="write_csv", action="store_true")
dest_group.add_argument(
    "--dest-workspace-id",
    dest="dest_workspace_id",
    type=str,
    help="Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000)",
)
dest_group.add_argument(
    "--dest-workspace-shared-key",
    dest="dest_workspace_shared_key",
    type=str,
    help="WARNING TEST ONLY. Log Analytics Workspace primary or secondary Connected Sources client authentication key (e.g. WW91IGJldHRlciBub3QgdXNlIHRoZSBzaGFyZWQga2V5IHlvdSBzb24gb2YgYSBiaXRjaCEhIQ==)",
)

dest_group.add_argument("--csv-dest-folder", dest="csv_dest_folder", type=str)

cli_group = parser.add_argument_group("CLI")

service_group = parser.add_argument_group("Service")
service_group.add_argument(
    "--iplist-update-interval",
    type=int,
    default=8,
    dest="iplist_update_interval",
    help="IP List update interval in Hours(H)",
)
service_group.add_argument(
    "--ip-analysis-interval",
    type=int,
    default=25,
    dest="ip_analysis_interval",
    help="IP List update interval in Seconds (S)",
)
