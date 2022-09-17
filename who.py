#!/usr/bin/python3

import io
import ipaddress
import json
import os
import shutil
import time
import zipfile
from gettext import find
from multiprocessing import Manager, Pool, cpu_count
from pathlib import Path

import requests
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import undefined
from git import Repo, exc
from pytz import utc

from libs.argument_parser import ParserOfArguments
import libs.global_vars as g_vars
from libs.inteligence import IntelligenceHandler
from libs.la_functions import post_data
from libs.logger import logging

log = logging.getLogger(os.path.basename(__file__))

g_vars.init()

g_vars.small_dic = True

# The log type is the name of the event that is being submitted
log_type_ipblock = "IPBlock"
log_type_ipwois = "IPWhoIs"
log_type_getnameinfo = "IPName"


def download_blocklists(git_dir=os.path.join("./", "blocklist-ipsets")):
    git_url = "https://github.com/firehol/blocklist-ipsets.git"
    zip_url = (
        "https://github.com/firehol/blocklist-ipsets/archive/refs/heads/master.zip"
    )
    try:
        log.info(f"Cloning: {git_url}")
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
        log.warning(f"Clone failed")
        log.warning(f"GETting: {zip_url}")
        r = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall()
        os.rename(git_dir + "-master", git_dir)


def read_file(file):
    log.info(f"Reading file: {file}")
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
        log.debug(f"File: {file} has {len(tmp_list)} entries")
        return tmp_list


def read_file_v2(file, d, ip_list_name):
    d[ip_list_name] = read_file(file)


def parse_dl_blocklists(git_dir):
    # global big_dic
    # global small_dic
    # big_dic = dict()
    g_vars.small_dic = True

    # manager = Manager()

    # d = manager.dict()
    tmp_list = list()
    import timeit

    with Pool(cpu_count()) as p:
        for i in os.listdir(git_dir):
            if "stopforumspam" in i:
                continue
            if "firehol" in i:
                continue
            file = os.path.join(git_dir, i)
            if os.path.isfile(file) is True and file.endswith((".ipset", ".netset")):
                ip_list_name = Path(file).stem
                # tmp_list.append((file, d, ip_list_name))
                starttime = timeit.default_timer()
                g_vars.big_dic[ip_list_name] = read_file(file)
                log.debug(
                    f"List {ip_list_name} took {timeit.default_timer() - starttime}s"
                )
                # print(p.map(f, [1, 2, 3]))
    #     p.starmap(read_file_v2, tmp_list)
    # big_dic = d.copy()
    g_vars.small_dic = False
    # raise


git_dir = os.path.join("./", "blocklist-ipsets")


def dowload_and_parse_blocklist(git_dir, skip_blocklist_download):
    if skip_blocklist_download:
        pass
    else:
        download_blocklists(git_dir)
    parse_dl_blocklists(git_dir)


#########################################################################################

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
    result = ih.check_getnameinfo()
    dh.commit(result, log_type=log_type_getnameinfo)


if __name__ == "__main__":
    
    args = ParserOfArguments(os.path.basename(__file__)).hombrew_parse()

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
