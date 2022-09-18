import argparse
import os


# Courtesy of http://stackoverflow.com/a/10551190 with env-var retrieval fixed
class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class ParserOfArguments:
    def __init__(self, main_name) -> None:
        parser = argparse.ArgumentParser(
            prog=main_name,
            description="A foo that bars",
            epilog="And that's how you'd foo a bar",
        )

        parser.add_argument(
            "--skip-blocklist-download",
            dest="skip_blocklist_download",
            action="store_true",
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
            action=EnvDefault,
            envvar="SOURCEWORKSPACEID",
            help="Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000).\n(env=SOURCEWORKSPACEID)",
        )
        source_group.add_argument(
            "--log-analutics-kusto",
            dest="log_analutics_kusto",
            type=str,
            action=EnvDefault,
            envvar="LOGANALYTICSKUSTO",
            help="Kusto query that returns IP list (e.g. Edge_CL | project clientIP | distinct clientIP).\n(env=LOGANALYTICSKUSTO)",
        )
        source_group.add_argument(
            "--log-analutics-timedelta",
            dest="log_analutics_timedelta",
            type=int,
            default=90,
            action=EnvDefault,
            envvar="LOGANALYTICSTIMEDELTA",
            help="Timedelta to search from present in minutes (M) (default 60 minutes).\n(env=LOGANALYTICSTIMEDELTA)",
        )
        source_group.add_argument("--csv-path", dest="csv_path", type=str)

        dest_group = parser.add_argument_group("Result Destination")
        dest_group2 = dest_group.add_mutually_exclusive_group(required=True)
        dest_group2.add_argument(
            "--write-log-analytics", dest="write_log_analytics", action="store_true"
        )
        dest_group2.add_argument("--write-csv", dest="write_csv", action="store_true")
        dest_group2.add_argument(
            "--write-blob-storage", dest="write_blob_storage", action="store_true"
        )
        dest_group.add_argument(
            "--dest-workspace-id",
            dest="dest_workspace_id",
            type=str,
            action=EnvDefault,
            envvar="DESTWORKSPACEID",
            help="Log Analytics Workspace ID (e.g. 00000000-0000-0000-0000-000000000000).\n(env=DESTWORKSPACEID)",
        )
        dest_group.add_argument(
            "--dest-workspace-shared-key",
            dest="dest_workspace_shared_key",
            type=str,
            action=EnvDefault,
            envvar="DESTWORKSPACESHAREDKEY",
            help="WARNING TEST ONLY. Log Analytics Workspace primary or secondary Connected Sources client authentication key (e.g. WW91IGJldHRlciBub3QgdXNlIHRoZSBzaGFyZWQga2V5IHlvdSBzb24gb2YgYSBiaXRjaCEhIQ==).\n(env=DESTWORKSPACESHAREDKEY)",
        )

        dest_group.add_argument(
            "--csv-dest-folder",
            dest="csv_dest_folder",
            type=str,
            help="NOT IMPLEMENTED",
        )
        dest_group3 = dest_group.add_mutually_exclusive_group(required=False)
        dest_group3.add_argument(
            "--storage-account-user-auth",
            dest="storage_account_user_auth",
            action="store_true",
            help="Enables user authentication using: ManagedIdentityCredential,	SharedTokenCacheCredential, VisualStudioCodeCredential, AzureCliCredential, AzurePowerShellCredential. Mutually exlusive",
        )
        dest_group3.add_argument(
            "--storage-account-service-auth",
            dest="storage_account_service_auth",
            action="store_true",
            help="Enables service authentication using storage account key. Mutually exlusive",
        )
        dest_group.add_argument(
            "--storage-account-container-name",
            dest="storage_account_container_name",
            type=str,
            action=EnvDefault,
            envvar="STORAGEACCOUNTCONTAINERNAME",
            help="(env=STORAGEACCOUNTCONTAINERNAME)",
            required=False,
        )
        dest_group.add_argument(
            "--storage-account-url",
            dest="storage_account_url",
            type=str,
            action=EnvDefault,
            envvar="STORAGEACCOUNTURL",
            help="Storage Account URL.\n(env=STORAGEACCOUNTURL)",
            required=False,
        )
        dest_group.add_argument(
            "--storage-account-key",
            dest="storage_account_key",
            type=str,
            action=EnvDefault,
            envvar="STORAGEACCOUNTKEY",
            help="Storage Account Key. Use with --storage-account-service-auth.\n(env=STORAGEACCOUNTKEY)",
            required=False,
        )

        cli_group = parser.add_argument_group("CLI")

        service_group = parser.add_argument_group("Service")
        service_group.add_argument(
            "--iplist-update-interval",
            type=int,
            default=8,
            dest="iplist_update_interval",
            action=EnvDefault,
            envvar="IPLISTUPDATEINTERVAL",
            help="IP List update interval in Hours (H).\n(env=IPLISTUPDATEINTERVAL)",
        )
        service_group.add_argument(
            "--ip-analysis-interval",
            type=int,
            default=600,
            dest="ip_analysis_interval",
            action=EnvDefault,
            envvar="IPANALYSISINTERVAL",
            help="IP List update interval in Seconds (S).\n(env=IPANALYSISINTERVAL)",
        )

        self.parser = parser

    def hombrew_parse(self):
        return self.parser.parse_args()
