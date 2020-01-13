# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import requests
import lxml.html

class ResponseHandler:
    _DISPATCH_AUDIO_XPATH = "//*[@id='call-log-info']//table/tr/td[1]/audio/@src"
    
    def __init__(self) -> None:
        self._parsing_successful:   bool                = None
        self._consecutive_failures: int                 = 0
        self._latest_response:      requests.Response   = None
    
    def extract_dispatch_call_relative_urls(self, *,
        response: requests.Response
    ) -> [str]:
        response_tree = lxml.html.fromstring(response.content)
        return response_tree.xpath(ResponseHandler._DISPATCH_AUDIO_XPATH)
