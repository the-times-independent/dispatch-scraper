# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import os
import urllib

class InternetFilePersister:
    def __init__(self, *,
        containing_directory: str,
        relative_url_prefix: str,
    ):
        self._containing_directory  = containing_directory
        self._relative_url_prefix   = relative_url_prefix
    
    def save_files_from_relative_urls(self, relative_urls: [str]):
        for relative_url in relative_urls:
            self.save_file_from_relative_url(relative_url)
    
    def save_file_from_relative_url(self, relative_url: str):
        filename = self._containing_directory + relative_url
        os.makedirs(
            os.path.dirname(filename),
            exist_ok = True,
        )
        urllib.request.urlretrieve(
            self._relative_url_prefix + relative_url,
            filename,
        )
