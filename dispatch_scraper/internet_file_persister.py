# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import os
import os.path
import urllib
import logging
import typing

class InternetFilePersister:
    def __init__(self, *,
        containing_directory: str,
        relative_url_prefix: str,
        overwrite_existing: bool = False,
    ):
        self._containing_directory  = containing_directory
        self._relative_url_prefix   = relative_url_prefix
        self._overwrite_existing    = overwrite_existing
        
        self._saved_file_paths: typing.List[str] = []
    
    def save_files_from_relative_urls(self, relative_urls: [str]):
        logging.info(f"saving {len(relative_urls)} calls")
        for relative_url in relative_urls:
            self.save_file_from_relative_url(relative_url)
    
    def save_file_from_relative_url(self, relative_url: str):
        logging.info(f"saving call at {relative_url}")
        file_path = self._containing_directory + relative_url
        
        if (not os.path.exists(file_path)) or self._overwrite_existing:
            self._save_file_core(file_path, relative_url)
    
    def _save_file_core(self, file_path, relative_url):
        os.makedirs(
            os.path.dirname(file_path),
            exist_ok = True,
        )
        urllib.request.urlretrieve(
            self._relative_url_prefix + relative_url,
            file_path,
        )
        self._saved_file_paths.append(file_path)
    
    def get_paths_of_saved_files(self) -> typing.List[str]:
        return self._saved_file_paths
