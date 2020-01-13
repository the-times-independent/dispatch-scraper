# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import requests
import logging
import lxml.html
import random
from ..response_handler import ResponseHandler

class ProxyRotator:
    STARTING_PROXY = "54.36.246.74:80"
    
    def __init__(self, *,
        logger: logging.Logger,
        starting_proxy          = STARTING_PROXY,
    ):
        self._logger = logger
        
        if starting_proxy != None:
            self._current_proxy = starting_proxy
            self._logger.info(f"using initial proxy {self._current_proxy}")
        else:
            self.get_new_proxy()
    
    def get_new_proxy(self) -> None:
        proxy_list_url = 'https://free-proxy-list.net/'
        response = requests.get(proxy_list_url)
        parser = lxml.html.fromstring(response.text)
        proxies = set()
        for row in parser.xpath('//*[@id="proxylisttable"]/tbody/tr'):
            proxy = ":".join([row.xpath('.//td[1]/text()')[0], row.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
        
        self._current_proxy = random.sample(proxies, 1)[0]
        self._logger.info(f"new proxy is {self._current_proxy}")
    
    def get_current_proxy(self) -> str:
        return self._current_proxy
