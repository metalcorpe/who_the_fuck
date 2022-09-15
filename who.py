import argparse
from multiprocessing import Manager, Pool, cpu_count
import time
import requests, zipfile, io
import asyncio
from gettext import find
import shutil
import whois
from whois_parser import WhoisParser
from ipwhois import IPWhois
from datetime import datetime, timedelta, timezone
import os
import pprint
from pathlib import Path
import ipaddress
import json
import hashlib
from git import Repo, exc
from azure.identity import DefaultAzureCredential
import hmac
import base64
from azure.monitor.query import LogsQueryClient
from azure.monitor.query import LogsQueryStatus
from azure.core.exceptions import HttpResponseError
import pandas as pd
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore, ConflictingIdError
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.util import undefined

from libs.la_functions import post_data
from libs.argument_parser import parser

global big_dic
global small_dic
small_dic = True

# The log type is the name of the event that is being submitted
log_type_ipblock = "IPBlock"
log_type_ipwois = "IPWhoIs"


def find_ip_in_blocklists(clientip):
    entry = dict()
    entry["cliIP"] = clientip
    try:
        ipobj = ipaddress.ip_address(clientip)
    except ValueError as e:
        print(clientip, str(e))
        entry["Total"] = 0
        return entry
    global small_dic
    try:
        while small_dic:
            time.sleep(15)
            print("sleeping")
    except:
        pass

    for i in big_dic.items():
        for j in i[1]:
            if ipobj in j:
                entry[i[0]] = str(j)

    entry["Total"] = len(entry) - 1
    return entry


def download_blocklists(git_dir=os.path.join("./", "blocklist-ipsets")):
    git_url = "https://github.com/firehol/blocklist-ipsets.git"
    zip_url = (
        "https://github.com/firehol/blocklist-ipsets/archive/refs/heads/master.zip"
    )
    try:
        shutil.rmtree(git_dir, ignore_errors=True)
        Repo.clone_from(git_url, git_dir, branch="master")
    except exc.GitCommandError as e:
        if (
            e.status == 128
            and "already exists and is not an empty directory" in e.stderr
        ):
            test = Repo(git_dir)
            test.remote().pull(allow_unrelated_histories=True)
        else:
            raise e
    except Exception as e:
        r = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall()
        os.rename(git_dir + "-master", git_dir)


def read_file(file):
    tmp_list = list()
    # print(Path(file).stem)
    with open(file, mode="r") as f:
        f_l = f.read().splitlines()
        f_l = [x for x in f_l if not x.startswith("#")]
        for line in f_l:
            try:
                ip = ipaddress.ip_network(line)
            except:
                raise
            else:
                tmp_list.append(ip)
        return tmp_list

def read_file_v2(file, d, ip_list_name):
    d[ip_list_name] = read_file(file)

def parse_dl_blocklists(git_dir):
    global big_dic
    global small_dic
    big_dic = dict()
    small_dic = True
    

    
    manager = Manager()

    d = manager.dict()
    tmp_list = list()
    import timeit

    with Pool(cpu_count()) as p:
            for i in os.listdir(git_dir):
                if "stopforumspam" in i:
                    continue
                file = os.path.join(git_dir, i)
                if os.path.isfile(file) is True and file.endswith((".ipset", ".netset")):
                    ip_list_name = Path(file).stem
                    # tmp_list.append((file, d, ip_list_name))
                    starttime = timeit.default_timer()
                    big_dic[ip_list_name] = read_file(file)
                    print(f"{ip_list_name};{timeit.default_timer() - starttime}")
                    # print(p.map(f, [1, 2, 3]))
    #     p.starmap(read_file_v2, tmp_list)
    # big_dic = d.copy()
    small_dic = False
    raise


git_dir = os.path.join("./", "blocklist-ipsets")


def dowload_and_parse_blocklist(git_dir, skip_blocklist_download):
    if skip_blocklist_download:
        pass
    else:
        download_blocklists(git_dir)
    parse_dl_blocklists(git_dir)


#########################################################################################
class IntelligenceHandler:
    def __init__(self, query, workspace_id, timedelta) -> None:
        self.workspace_id = workspace_id
        self.query = query
        self.timedelta = timedelta
        self.credential = DefaultAzureCredential()
        self.logs_client = LogsQueryClient(self.credential)
        self.iplist = list()
        pass

    def query_space(self):
        start_time = datetime(2022, 8, 31, tzinfo=timezone.utc)
        end_time = datetime(2022, 8, 30, tzinfo=timezone.utc)

        try:
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=self.query,
                timespan=timedelta(minutes=self.timedelta),
                # timespan=(start_time, end_time),
            )
            if response.status == LogsQueryStatus.PARTIAL:
                error = response.partial_error
                data = response.partial_data
                print(error.message)
            elif response.status == LogsQueryStatus.SUCCESS:
                data = response.tables
            table = data[0]
            df = pd.DataFrame(data=table.rows, columns=table.columns)
            self.iplist = list(df.cliIP_s.unique())

        except HttpResponseError as err:
            print("something fatal happened")
            print(err)

    def check_blocklist(self):
        result = list()
        for ip in self.iplist:
            ret = find_ip_in_blocklists(ip)
            if ret["Total"] == 0:
                continue
            result.append(ret)
        return result

    def check_ipwhois(self):
        result = list()
        for ip in self.iplist:
            ip_result = IPWhois(ip)
            ret = ip_result.lookup_rdap(depth=0)
            result.append(ret)
        return result


# hostname = "1.1.1.1"
# hostname = "8.8.8.8"
# hostname = "tavani.mooo.com"
# hostname = "46.198.200.167"
# hostname = "5.54.71.210"
# domain = whois.whois(hostname)

# parser = WhoisParser()
# record = parser.parse(domain.text, hostname=hostname)
# print(record)
class LAHandler:
    def __init__(self, workspace_id, shared_key) -> None:
        self.workspace_id = workspace_id
        self.shared_key = shared_key

    def send(self, result, log_type):
        body = json.dumps(result)
        post_data(self.workspace_id, self.shared_key, body, log_type)


class CSVHandler:
    def __init__(self) -> None:
        pass

    def send(self, result, log_type):
        pass


class DestinationHandler:
    def __init__(self, args) -> None:
        if args.write_log_analytics:
            self.handler = LAHandler(
                args.dest_workspace_id, args.dest_workspace_shared_key
            )
        elif args.write_csv:
            self.handler = CSVHandler()
            raise NotImplementedError
        else:
            raise NotImplementedError

    def commit(self, result, log_type):
        self.handler.send(result, log_type)


def poll_source(args):
    ih = IntelligenceHandler(
        args.log_analutics_kusto, args.source_workspace_id, args.log_analutics_timedelta
    )
    dh = DestinationHandler(args)
    ih.query_space()
    result = ih.check_blocklist()
    dh.commit(result, log_type=log_type_ipblock)
    result = ih.check_ipwhois()
    dh.commit(result, log_type=log_type_ipwois)


if __name__ == "__main__":
    # import logging

    # from opencensus.ext.azure.log_exporter import AzureEventHandler

    # logger = logging.getLogger(__name__)
    # # TODO: replace the all-zero GUID with your instrumentation key.
    # logger.addHandler(AzureEventHandler(
    #     connection_string='InstrumentationKey=85d74f7f-38ff-40cc-b996-8adfaff95b4e')
    # )

    # properties = {'custom_dimensions': {'key_1': 'value_1', 'key_2': 'value_2'}}

    # # Use properties in logging statements
    # logger.warning('action_event_key', extra=properties)
    # parser.print_help()
    args = parser.parse_args()

    if args.service:

        jobstores = {"default": MemoryJobStore()}
        job_defaults = {"coalesce": False, "max_instances": 5}
        executors = {
            "default": ThreadPoolExecutor(20),
            "processpool": ProcessPoolExecutor(5),
        }

        scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=utc,
        )

        scheduler.start()
        # scheduler.add_job(
        #     dowload_and_parse_blocklist,
        #     args=[git_dir, args.skip_blocklist_download],
        #     trigger=IntervalTrigger(hours=args.iplist_update_interval),
        #     id="blocklist-ipsets",
        #     name="blocklist-ipsets",
        #     coalesce=True,
        #     max_instances=1,
        #     # next_run_time=undefined if os.path.exists(git_dir) else datetime.utcnow(),
        # )
        # scheduler.add_job(
        #     poll_source,
        #     args=[args],
        #     trigger=IntervalTrigger(seconds=args.ip_analysis_interval),
        #     id="ip-analysis",
        #     name="ip-analysis",
        #     coalesce=True,
        #     max_instances=1,
        #     # next_run_time=undefined if os.path.exists(git_dir) else datetime.utcnow(),
        # )

        dowload_and_parse_blocklist(git_dir, args.skip_blocklist_download)
        poll_source(args)
        try:
            while True:
                # poll interval in seconds
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.shutdown()
        except Exception as ex:
            raise

    elif args.cli:
        raise NotImplementedError
    else:
        raise NotImplementedError
