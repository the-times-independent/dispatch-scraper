# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import requests
import logging
import lxml.html
from pape.utilities import ordinal
from ..response_handler import ResponseHandler
from .proxy_rotator import ProxyRotator
from ..internet_file_persister import InternetFilePersister

class Requester:
    _DISPATCH_CALL_LOG_URL          = "https://www.edispatches.com/call-log/index.php"
    _DISPATCH_SCRAPER_USER_AGENT    = (
        "DispatchScraper/0.1.0 (+https://github.com/the-times-independent/dispatch-scraper)"
    )
    _DISPATCH_CALL_LOG_FORM_DATA    = {
        "ddl-state":    "UT",
        "ddl-county":   "Grand",
        "ddl-company":  "ALL",
        "ddl-limit":    "ALL",
    }
    
    CONSECUTIVE_FAILURES_THRESHOLD  = 2
    REQUEST_TIMEOUT_IN_SECONDS      = 10
    
    def __init__(self, *,
        logger: logging.Logger,
        response_handler: ResponseHandler,
        internet_file_persister: InternetFilePersister,
    ):
        self._consecutive_failures_threshold    = Requester.CONSECUTIVE_FAILURES_THRESHOLD
        self._request_timeout_in_seconds        = Requester.REQUEST_TIMEOUT_IN_SECONDS
        
        self._logger                    = logger
        self._response_handler          = response_handler
        self._internet_file_persister   = internet_file_persister
        
        self._do_try_again          = True
        self._consecutive_failures  = 0
        self._response              = None
        self._petition_url          = Requester._DISPATCH_CALL_LOG_URL
        self._request_headers       = {
            "User-Agent": Requester._DISPATCH_SCRAPER_USER_AGENT,
        }
        self._proxy_rotator     = ProxyRotator(
            logger = self._logger,
        )
    
    def get_then_process_call_log(self):
        self._request_page()
        relative_urls = self._response_handler.extract_dispatch_call_relative_urls(
            response = self._response,
        )
        self._internet_file_persister.save_files_from_relative_urls(relative_urls)
    
    def _request_page(self):
        self._logger.info("sending request")
        self._response = requests.post(
            self._petition_url,
            headers = self._request_headers,
            timeout = 10,
            data = Requester._DISPATCH_CALL_LOG_FORM_DATA,
        )
        
        self._response.raise_for_status()
