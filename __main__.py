#!/usr/bin/env python

# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import logging, sys

from argparse import ArgumentParser
from dispatch_scraper import DispatchScraper

argument_parser = ArgumentParser(
    description = "for scraping the eDispatches call log",
)

argument_parser.add_argument(
    "-d", "--call-directory",
    dest = "call_directory_path",
    type = str,
    help = "directory for reading and writing dispatch call recordings",
    default = "./dispatches",
)

argument_parser.add_argument(
    "-v", "--verbosity",
    dest = "log_verbosity",
    help = "set logging verbosity",
    choices = logging._nameToLevel.keys(),
    default = DispatchScraper._DEFAULT_LOGGING_LEVEL,
    type = str
)

arguments = argument_parser.parse_args()

scraper = DispatchScraper(
    name_list_file_path = arguments.name_list_file_path,
    log_verbosity = arguments.log_verbosity,
    consecutive_failures_threshold = arguments.consecutive_failures_threshold,
    average_wait_time = arguments.average_wait_time,
    request_timeout = arguments.request_timeout,
    first_proxy = arguments.first_proxy,
)

scraper.run()
