import ipaddress
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from socket import gaierror, getnameinfo

import pandas as pd
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from ipwhois import IPWhois
from pytz import utc

import libs.global_vars as g_vars
from libs.logger import logging

log = logging.getLogger(os.path.basename(__file__))

def find_ip_in_blocklists(clientip):
    # global small_dic
    # global big_dic
    entry = dict()
    entry["cliIP"] = clientip
    try:
        ipobj = ipaddress.ip_address(clientip)
    except ValueError as e:
        print(clientip, str(e))
        entry["Total"] = 0
        return entry
    try:
        while g_vars.small_dic:
            time.sleep(15)
            print("sleeping")
    except:
        pass
    for i in g_vars.big_dic.items():
        for j in i[1]:
            if ipobj in j:
                entry[i[0]] = str(j)

    entry["Total"] = len(entry) - 1
    return entry

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
            log.debug(f'{sys._getframe(  ).f_code.co_name}: {ret}')
            result.append(ret)
        return result

    def check_ipwhois(self):
        result = list()
        for ip in self.iplist:
            ip_result = IPWhois(ip)
            ret = ip_result.lookup_rdap(depth=0)
            ret["cliIP"] = ip
            log.debug(f'{sys._getframe(  ).f_code.co_name}: {ret}')
            result.append(ret)
        return result

    def check_getnameinfo(self):
        result = list()
        for ip in self.iplist:
            try:
                ip_result = getnameinfo((ip, 0), 0)
            except gaierror:
                continue
            ret = dict()
            ret['nameinfo'] = ip_result[0]
            ret["cliIP"] = ip
            if ret['cliIP'] == ret['nameinfo']:
                continue
            log.debug(f'{sys._getframe(  ).f_code.co_name}: {ret}')
            result.append(ret)
        return result
