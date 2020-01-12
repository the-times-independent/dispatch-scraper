# # # # # # # # # # # # # # # # # # # #
# Dispatch Scraper, a journalism tool
# Copyright 2020 Carter Pape
# 
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

import requests, re, stem, stem.control, lxml.html, time, random, os, logging, sys, datetime
from pape.utilities import ordinal
import datetime

class DispatchScraper:
    _DISPATCH_CALL_LOG_URL                  = "https://www.edispatches.com/call-log/index.php"
    _DISPATCH_AUDIO_XPATH                   = "//*[@id='call-log-info']//table/tr/td[1]/audio/@src"
    
    _DEFAULT_CONSECUTIVE_FAILURES_THRESHOLD = 2
    _DEFAULT_AVERAGE_WAIT_TIME_IN_SECONDS   = 5
    _DEFAULT_LOGGING_LEVEL                  = "INFO"
    _DEFAULT_REQUEST_TIMEOUT_IN_SECONDS     = 10
    _DEFAULT_FIRST_PROXY                    = "54.36.246.74:80"
    
    
    
    def __init__(
        self, *,
        name_list_file_path,
        log_verbosity                   = _DEFAULT_LOGGING_LEVEL,
        consecutive_failures_threshold  = _DEFAULT_CONSECUTIVE_FAILURES_THRESHOLD,
        average_wait_time               = _DEFAULT_AVERAGE_WAIT_TIME_IN_SECONDS,
        request_timeout                 = _DEFAULT_REQUEST_TIMEOUT_IN_SECONDS,
        first_proxy                     = _DEFAULT_FIRST_PROXY,
    ):
        
        self._petition_url = "https://www.edispatches.com/call-log/index.php"
        self._request_headers = {
            "User-Agent":
                "DispatchScraper/0.1.0 "
                "(+https://github.com/the-times-independent/dispatch-scraper)",
        }
        
        self._name_list_file_path               = name_list_file_path
        self._consecutive_failures_threshold    = consecutive_failures_threshold
        self._average_wait_time: float          = average_wait_time
        
        self._logger = logging.Logger(
            "petition scraping logger",
            level = log_verbosity,
        )
        
        self._logger.addHandler(
            logging.StreamHandler(stream = sys.stdout)
        )
        
        self._parsing_successful:   bool                = None
        self._consecutive_failures: int                 = 0
        self._latest_response:      requests.Response   = None
        
        self._total_signers_count_adjusted: int = None
        self._found_signers:                set = None
        self._previous_found_signers:       set = None
        
        if first_proxy != None:
            self._current_proxy = first_proxy
            self._logger.info(f"using initial proxy {first_proxy}")
        else:
            self._get_new_proxy()
    
    def run(self):
        self._get_existing_names()
        
        self._logger.info(f"starting with {len(self._found_signers)} names")
        
        while True:
            self._do_a_request()
            
            if self._all_names_collected():
                self._logger.info("job done (for now)")
                break
        
    
    def _do_a_request(self):
        try:
            self._request_page()
            self._extract_items()
        except lxml.etree.ParserError as the_exception:
            self._logger.error("error while parsing HTML tree: " + str(the_exception))
            self._avoid_per_ip_ban()
        except HTTPErrorCodeReturnedError as the_exception:
            self._logger.error(f"HTTP code {the_exception.status_code} returned")
            if the_exception.status_code == 429:
                self._get_new_proxy()
            else:
                self._avoid_per_ip_ban()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ) as the_exception:
            self._logger.error("error while requesting page: " + str(the_exception))
            self._avoid_per_ip_ban()
        except requests.exceptions.ReadTimeout as the_exception:
            self._logger.error("The request timed out; details: " + str(the_exception))
            self._avoid_per_ip_ban()
        except requests.exceptions.TooManyRedirects as the_exception:
            self._logger.error("too many redirects (probably a bad proxy); details: " + str(the_exception))
            self._get_new_proxy()
        else:
            self._record_names()
            self._reset_consecutive_failures()
            self._throttle()
                
    
    def _get_existing_names(self):
        if (not os.path.isfile(self._name_list_file_path)):
            self._logger.info(f"file '{self._name_list_file_path}' not found; skipping import step")
            self._found_signers             = set()
            self._previous_found_signers    = set()
            return
            
        name_list = [
                line.rstrip("\n")
            for line in open(self._name_list_file_path)
        ]
        
        self._found_signers             = set(name_list[1:])
        self._previous_found_signers    = self._found_signers.copy()
    
    def _request_page(self):
        self._logger.info("\nsending new request")
        self._latest_response = requests.get(
            self._petition_url,
            headers = self._request_headers,
            proxies = {"http": f"http://{self._current_proxy}"},
            timeout = 10,
        )
        
        if self._latest_response.status_code > 400:
            raise HTTPErrorCodeReturnedError(
                status_code = self._latest_response.status_code,
                the_page = self._petition_url
            )
    
    def _throttle(self):
        wait_time = random.uniform(
            self._average_wait_time * 0.5,
            self._average_wait_time * 1.5,
        )
        self._logger.info(f"waiting {wait_time} seconds for next request")
        time.sleep(wait_time)
    
    def _extract_items(self):
        self._extract_html_tree()
        self._extract_total_signers_count()
        self._extract_twenty_signers()
    
    def _extract_html_tree(self):
        self._latest_response_tree = lxml.html.fromstring(self._latest_response.content)
    
    def _extract_total_signers_count(self):
        total_signers_count_text    = self._latest_response_tree.xpath(PetitionCrawler._SIGNER_COUNT_XPATH)[0]
        matches_for_count_regex     = re.match(r"\(20 of (\d+) total signers", total_signers_count_text)
        
        new_total_signers_count_unadjusted = int(matches_for_count_regex.groups()[0])
        new_total_signers_count_adjusted = (
            new_total_signers_count_unadjusted
            + PetitionCrawler._TOTAL_SIGNERS_ADJUSTMENT
        )
        
        if new_total_signers_count_adjusted != self._total_signers_count_adjusted:
            self._logger.info(f"The petition claims {new_total_signers_count_unadjusted} total signers.")
            self._logger.info(f"The crawler will stop at {new_total_signers_count_adjusted} names.")
            self._logger.info(f"The number of names already found is {len(self._found_signers)}.")
            self._total_signers_count_adjusted = new_total_signers_count_adjusted
    
    def _extract_twenty_signers(self):
        twenty_signers = self._latest_response_tree.xpath(PetitionCrawler._TWENTY_SIGNERS_XPATH)[:20]

        for name in twenty_signers:
            self._found_signers.add(name.strip())
    
    def _record_names(self):
        new_names = self._found_signers.difference(self._previous_found_signers)
        if len(new_names) == 0:
            self._logger.info(f"no new names found")
        else:
            self._logger.info(f"found {len(new_names)} new names: {new_names}")
            self._save_names()
            self._previous_found_signers = self._found_signers.copy()
        
        self._logger.info(
            f"still looking for "
            f"{self._total_signers_count_adjusted - len(self._found_signers)} more names"
        )
    
    def _save_names(self):
        with open(self._name_list_file_path, "w") as name_list_file:
            name_list = list(self._found_signers)
            name_list.sort(key = str.lower)
            name_list_file.write(
                f"{str(len(name_list))} signers (of {self._total_signers_count_adjusted} total "
                f"as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}):\n"
            )
            for name in name_list:
                name_list_file.write(name + "\n")
    
    def _avoid_per_ip_ban(self):
        self._consecutive_failures += 1
        
        self._logger.warning(
            f"Page retrieval failed. "
            f"This is the {ordinal(self._consecutive_failures)} consecutive failure with the current proxy."
        )
        
        if self._consecutive_failures >= self._consecutive_failures_threshold:
            self._logger.info(f"too many consecutive failures; rotating proxy")
            self._get_new_proxy()
        else:
            self._throttle()
    
    def _all_names_collected(self):
        if self._total_signers_count_adjusted == None:
            return False
        else:
            return len(self._found_signers) >= self._total_signers_count_adjusted
            
    def _get_new_proxy(self):
        proxy_list_url = 'https://free-proxy-list.net/'
        response = requests.get(proxy_list_url)
        parser = lxml.html.fromstring(response.text)
        proxies = set()
        for row in parser.xpath('//*[@id="proxylisttable"]/tbody/tr'):
            proxy = ":".join([row.xpath('.//td[1]/text()')[0], row.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
        
        self._current_proxy = random.sample(proxies, 1)[0]
        self._logger.info(f"new proxy is {self._current_proxy}")
        self._reset_consecutive_failures()
    
    def _reset_consecutive_failures(self):
        if self._consecutive_failures > 0:
            self._consecutive_failures = 0
            self._logger.info(f"consecutive failures reset to 0")
