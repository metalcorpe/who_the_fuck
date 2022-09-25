import ipaddress
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from socket import gaierror, getnameinfo

import pandas as pd
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from dns import exception, resolver, reversename
from ipwhois import IPWhois

import libs.global_vars as g_vars
from libs.logger import logging

log = logging.getLogger(os.path.basename(__file__))


def find_ip_in_blocklists(clientip):
    entry = dict()
    entry["cliIP"] = clientip
    try:
        ipobj = ipaddress.ip_address(clientip)
    except ValueError:
        raise
    try:
        while g_vars.small_dic:
            time.sleep(15)
            log.warn("Blocklist does not exist yet. Sleeping...")
    except:
        pass
    for i in g_vars.big_dic.items():
        for j in i[1]:
            if ipobj in j:
                entry[i[0]] = str(j)

    entry["Total"] = len(entry) - 1
    assert entry["Total"] != 0
    return entry


def find_ip_in_rdap(ip):
    ip_result = IPWhois(ip)
    # ret = ip_result.lookup_rdap(depth=0)
    ret = ip_result.lookup_whois()
    ret["cliIP"] = ip
    return ret


def get_name_info(ip):
    try:
        ip_result = getnameinfo((ip, 0), 0)
    except gaierror as e:
        raise e
    ret = dict()
    ret["nameinfo"] = ip_result[0]
    ret["cliIP"] = ip
    assert ret["cliIP"] != ret["nameinfo"]
    return ret


def get_name_info_v2(ip):
    try:
        rev_name = reversename.from_address(ip)
        my_resolver = resolver.Resolver()

        my_resolver.nameservers = ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
        ip_result = str(my_resolver.query(rev_name, "PTR")[0])
    except gaierror:
        raise exception.DNSException
    except resolver.NXDOMAIN as e:
        raise exception.DNSException
    except (exception.Timeout, resolver.NoNameservers, resolver.NoAnswer) as e:
        raise exception.DNSException
    except Exception as e:
        raise exception.DNSException
    ret = dict()
    ret["nameinfo"] = ip_result
    ret["cliIP"] = ip
    if ret["cliIP"] == ret["nameinfo"]:
        raise exception.DNSException
    return ret


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
        log.info(f"Quering Space")

        try:
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id,
                query=self.query,
                timespan=timedelta(minutes=self.timedelta),
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
            log.info(f"Kusto Result: {len(self.iplist)}")

        except HttpResponseError as err:
            print("something fatal happened")
            print(err)

    def check_blocklist(self):
        result = list()
        with ThreadPoolExecutor() as executor:
            future_to_url = {
                executor.submit(find_ip_in_blocklists, ip) for ip in self.iplist
            }

            for future in as_completed(future_to_url):
                try:
                    ret = future.result()
                    log.debug(f"{sys._getframe(  ).f_code.co_name}: Results{ret}")
                    result.append(ret)
                except Exception as e:
                    print("Looks like something went wrong:", e)
        return result

    def check_ipwhois(self):
        result = list()
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(find_ip_in_rdap, ip) for ip in self.iplist}

            for future in as_completed(future_to_url):
                try:
                    ret = future.result()
                    log.debug(f"{sys._getframe(  ).f_code.co_name}: Results{ret}")
                    result.append(ret)
                except Exception as e:
                    print("Looks like something went wrong:", e)

        return result

    def check_getnameinfo(self):
        result = list()
        with ThreadPoolExecutor() as executor:
            future_to_url = {
                executor.submit(get_name_info_v2, ip) for ip in self.iplist
            }

            log.debug(
                f"{sys._getframe(  ).f_code.co_name}: Looping over resulting tasks"
            )
            for future in as_completed(future_to_url):
                try:
                    ret = future.result()
                    log.debug(f"{sys._getframe(  ).f_code.co_name}: Results{ret}")
                    result.append(ret)
                except Exception as e:
                    print("Looks like something went wrong:", e)

        return result
