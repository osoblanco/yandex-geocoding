import pandas as pd
import requests
from lxml.html import fromstring
from itertools import cycle
import traceback
import random
import multiprocessing
from bs4 import BeautifulSoup
import collections
from fake_useragent import UserAgent


ua = UserAgent()
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:400]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return list(proxies)


proxies = get_proxies()
proxy_pool = cycle(proxies)

def full_query_dataset(dataset):
    dataset = {}
    try:
        for index, row in dataset.iterrows():
            potential_string = ''
            for count,key in enumerate(row):
                if count != 0 and count <=5:
                    potential_string +=" " + key

            potential_string = potential_string.strip()
            url = 'https://geocode-maps.yandex.ru/1.x/?geocode='+potential_string+"&lang=en-US"

            dataset[index] = url

    except Exception as e:
        print(e)

    return dataset

def get_yandex_url(location):
    url = ''
    try:
        url = 'https://geocode-maps.yandex.ru/1.x/?geocode='+location+"&lang=en-US"
    except Exception as e :
        return None

    return url

def list_segmentor(seq, size):
    newseq = []
    splitsize = 1.0/max(1,size)*len(seq)
    for i in range(size):
            newseq.append(seq[int(round(i*splitsize)):int(round((i+1)*splitsize))])
    return newseq

def list_enricher(core_dict, enrichemnt_list, iterator,return_dict):
    try:
        data_from_proc = []
        for index in enrichemnt_list[iterator]:
           # if index %100 == 0:
            #    print(index)

            content = geocode_enricher(core_dict[index], index)
            data_from_proc.append(content)

        return_dict[iterator] = data_from_proc

    except Exception as e:
        print(traceback.format_exc())#"error: "+str(e))

    return None


def parallel_runner(process_number):
    # Run tasks using processes
    core_dict = full_query_dataset()
    segmented_list = list_segmentor(list(locs.index.values),process_number)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    processes = [multiprocessing.Process(target = list_enricher, args = ([core_dict,segmented_list,iterator, return_dict])) for iterator in range(process_number)]
    [process.start() for process in processes]
    [process.join() for process in processes]

    ordered_parse = collections.OrderedDict(sorted(return_dict.items()))
    data = []
    for k, v in ordered_parse.items():
        data += v

    return data

def geocode_enricher(location,index=None):
    try:
        '''
        potential_string = potential_string.strip()
        url = potential_string.encode('utf8')
        url = urllib.parse.quote(url)

        print(url)
        url = 'https://geocode-maps.yandex.ru/1.x/?geocode='+url

        with urlopen(url) as response:
            html = response.read()
        '''

        long = None
        lat = None

        url = get_yandex_url(location)
        #context_dict = {str(locs.loc[index]['id']): [long,lat]}
        context_dict = {"Normalized Location":None, "long":long, "lat":lat}

        headers = {'User-Agent': ua.random}

        proxy = random.choice(proxies)
        proxy_dict = {}
        if 'https' in proxy:
            proxy_dict["https"] = proxy
        else:
            proxy_dict["http"] = proxy


        r = requests.get(url, proxies=proxy_dict, headers = headers, timeout=3)
        rawSource = str(r.content)


        if(not "Page Not Found" in rawSource):
            soup = BeautifulSoup(rawSource,'lxml')
            longlat = soup.findAll("pos")
            long, lat = str(longlat[0]).split(" ")
            long = long.replace("<pos>", "")
            lat = lat.replace("</pos>","")

            full_adress_line = soup.findAll("text")
            full_adress_line = str(full_adress_line)
            full_adress_line = full_adress_line.replace("</text>","")
            full_adress_line = full_adress_line.replace("<text>", "")



        context_dict["Normalized Location"] = full_adress_line
        context_dict['long'] = long
        context_dict['lat'] = lat
        #db.save(context_dict)

    except Exception as e:
        print(traceback.format_exc())
        print("Skipping entry with id: "+str(index))
        #return  {str(locs.loc[index]['id']): [None,None]}
        return {"Status":2,"Error": str(e)}

    #return {str(locs.loc[index]['id']): [long,lat]}
    return context_dict
