# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import logging
import sys
from .requester                 import Requester
from .response_handler          import ResponseHandler
from .internet_file_persister   import InternetFilePersister

class DispatchScraper:
    LOGGING_LEVEL = "INFO"
    
    def __init__(
        self, *,
        dispatch_directory_path: str,
    ):
        self._logger = logging.Logger(
            f"logger for {self}",
            level = DispatchScraper.LOGGING_LEVEL,
        )
        
        self._logger.addHandler(
            logging.StreamHandler(stream = sys.stdout),
        )
        
        self._response_handler  = ResponseHandler()
        self._internet_file_persister   = InternetFilePersister(
            containing_directory    = dispatch_directory_path,
            relative_url_prefix     = "https://www.edispatches.com",
        )
        self._requester         = Requester(
            logger                  = self._logger,
            response_handler        = self._response_handler,
            internet_file_persister = self._internet_file_persister
        )
    
    def run(self):
        self._requester.get_then_process_call_log()
