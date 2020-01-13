#!/usr/bin/env python

# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import logging
import sys
import os

from argparse                           import ArgumentParser
from dispatch_scraper                   import DispatchScraper
from dispatch_scraper.requester         import Requester
from dispatch_scraper.response_handler  import ResponseHandler

argument_parser = ArgumentParser(
    description = "for scraping the eDispatches call log",
)

argument_parser.add_argument(
    "-d", "--dispatch-directory",
    dest = "dispatch_directory_path",
    type = str,
    help = "directory for reading and writing dispatch call recordings",
    default = "./dispatches/",
)

argument_parser.add_argument(
    "-v", "--verbosity",
    dest = "log_verbosity",
    help = "set logging verbosity",
    choices = logging._nameToLevel.keys(),
    default = DispatchScraper.LOGGING_LEVEL,
    type = str
)

argument_parser.add_argument(
    "-f", "--failure-threshold",
    dest = "consecutive_failures_threshold",
    help = "number of consecutive page retrieval failures before killing the crawler",
    default = Requester.CONSECUTIVE_FAILURES_THRESHOLD,
)

argument_parser.add_argument(
    "-t", "--request-timeout-in-seconds",
    dest = "request_timeout_in_seconds",
    help = "longest time (in seconds) to wait before abandoning a request",
    default = Requester.REQUEST_TIMEOUT_IN_SECONDS,
)

arguments = argument_parser.parse_args()

DispatchScraper.LOGGING_LEVEL               = arguments.log_verbosity
Requester.CONSECUTIVE_FAILURES_THRESHOLD    = arguments.consecutive_failures_threshold
Requester.REQUEST_TIMEOUT_IN_SECONDS        = arguments.request_timeout_in_seconds

scraper = DispatchScraper(
    dispatch_directory_path = os.path.abspath(arguments.dispatch_directory_path)
)

scraper.run()
