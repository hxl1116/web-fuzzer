"""
:author: Henry Larson
:description: automatic web scraping class for discovery and testing operations
"""

from mechanicalsoup import StatefulBrowser
from collections import namedtuple
from requests.exceptions import Timeout
from urllib import parse

DISCOVERED_PAGES = namedtuple('DiscoveredPages', ['paths', 'links', 'visited'])
DISCOVERED_INPUTS = namedtuple('DiscoveredInputs', ['params', 'fields', 'cookies'])
TEST_RESULTS = namedtuple('TestResults', ['code', 'status', 'leaked', 'dirty', 'timeout'])


# TODO: Refactor return formats
class FuzzScraper:
    """
    Class used to find and scrape valid web addresses, inputs, and cookies
    """
    paths = {'log': 'login.php', 'set': 'setup.php', 'idx': 'index.php', 'sec': 'security.php'}
    blacklist = ['http://se.rit.edu', 'http://localhost:80/logout.php']

    def __init__(self):
        """
        Initializes the Browser object
        """
        self.browser = StatefulBrowser()
        self.base_url = ''

        # 'discover' mode attributes
        self.valid_paths = {'guessed': [], 'discovered': []}
        self.valid_links = []
        self.visited_paths = []

        self.discovered_params = {}
        self.discovered_fields = {}
        self.discovered_cookies = []

        # 'test' mode attributes
        self.timeout = 0
        self.vectors = []
        self.sensitive = []
        self.sanitized_chars = []

        self.test_results = {}

    def contains_dirty_data(self, data):
        # TODO: Docstrings
        return [char for char in self.sanitized_chars if str(char).casefold() in str(data).casefold()]

    def contains_sensitive_data(self, data):
        # TODO: Docstrings
        return [word for word in self.sensitive if str(word).casefold() in str(data).casefold()]

    def clean_stored_data(self):
        # FIXME: Removes full web addresses
        """
        Removes duplicate entries by converting the data lists to dicts and back

        :return: None
        """
        self.valid_paths = list(dict.fromkeys(self.valid_paths))
        self.valid_links = list(dict.fromkeys(self.valid_paths))
        self.visited_paths = list(dict.fromkeys(self.visited_paths))

    def compile_inputs(self):
        """
        Provides all discovered inputs from the 'discovered_params', 'discovered_fields', and 'discovered_cookies'
        attributes

        :return: namedtuple(params=<discovered params>, fields=<discovered fields>, cookies=<discovered cookies>)
        """
        return DISCOVERED_INPUTS(params=self.discovered_params,
                                 fields=self.discovered_fields,
                                 cookies=self.discovered_cookies)

    def compile_pages(self):
        """
        Provides all discovered pages from the 'valid_paths', 'valid_links', and 'visited_paths' attributes

        :return: namedtuple(paths=<valid paths>, links=<valid links>, visited=<visited paths>)
        """
        return DISCOVERED_PAGES(paths=self.valid_paths, links=self.valid_links, visited=self.visited_paths)

    def discover_cookies(self):
        """
        Gets the cookies from the validated paths

        :return: None
        """
        return self.browser.get_cookiejar()

    def discover_form_fields(self):
        # TODO: Docstrings
        form_fields = {}

        for path in self.valid_paths['guessed'] + self.valid_paths['discovered']:
            self.navigate(path)
            header = self.browser.get_current_page().find('h1')
            inputs = [field for field in self.browser.get_current_page().find_all('input')
                      if field['type'] not in ['button', 'submit']]

            if inputs:
                form_fields[header.text if header else path] = inputs

        return form_fields

    def discover_inputs(self):
        """
        Calls URL parameter, form input field, and browser cookie discovery functions.
        Assigns results to 'discovered_params', 'discovered_fields', and 'discovered_cookies' attributes, respectively

        :return: None
        """
        self.discovered_params = self.discover_url_params()
        self.discovered_fields = self.discover_form_fields()
        self.discovered_cookies = self.discover_cookies()

    def discover_url_params(self):
        # TODO: Docstrings
        guessed_params = {path: parse.urlparse('%s/%s' % (self.base_url, path)).query
                          for path in self.valid_paths['guessed']}
        discovered_params = {path: parse.urlparse('%s/%s' % (self.base_url, path)).query
                             for path in self.valid_paths['discovered']}

        return {path: params for path, params in {**guessed_params, **discovered_params}.items() if params != ''}

    def find_links(self, url='.'):
        """
        Recursively finds link tags on valid webpages

        :param url: discovered link
        :return: None
        """

        if str(url).endswith('.pdf'):
            self.valid_links.append(url)
            return
        if str(url).startswith('../'):
            return
        if str(url).__contains__('logout'):
            return

        self.valid_links.append(url)

        if url not in self.visited_paths:
            self.navigate_and_save(url)  # Save URL to discovered paths
            if url in self.valid_paths['guessed'] or url in self.valid_paths['discovered']:
                self.visited_paths.append(url)  # Save URL to visited paths

                # Recurse through discovered links
                [self.find_links(link['href']) for link in self.browser.links()]

                # Recurse through guessed valid paths
                [self.find_links(link) for link in self.valid_paths['guessed']]

                # Recurse through discovered valid paths
                [self.find_links(link) for link in self.valid_paths['discovered']]
            else:
                return
        else:
            return

    def is_blacklisted(self, path):
        """
        Determines if a provided path is contained in the blacklist

        :param path: provided path
        :return: True or False
        """
        for site in self.blacklist:  # Ignore blacklisted sites
            if '%s/%s' % (self.base_url, path) == site:
                return True

    def login(self, credentials):
        """
        Submits the login credentials for DVWA

        :param credentials: provided login credentials
        :return: None
        """
        self.navigate_and_save(path_key='set')
        self.browser.select_form()
        self.browser.submit_selected()

        self.navigate_and_save(path_key='log')
        self.browser.select_form().set_input(credentials)
        self.browser.submit_selected()

    def navigate(self, path=None, path_key=None):
        """
        Opens the Browser object to a specified path

        :param path: given path
        :param path_key: key to a path in the 'paths' dict
        :return: None
        """
        if path_key:
            self.browser.open('%s/%s' % (self.base_url, self.paths[path_key]))
        if path:
            if self.is_blacklisted(path):
                return
            else:
                self.browser.open('%s/%s' % (self.base_url, path))
        else:
            return

    def navigate_and_save(self, path=None, path_key=None, guessed=False):
        # TODO: Combine with 'navigate'
        """
        Opens the Browser to a specified path and saves the path if it is valid

        :param path: given path
        :param path_key: key to a path in the 'paths' dict
        :param guessed: if the path is guessed
        :return: None
        """
        if path_key:
            res = self.browser.open('%s/%s' % (self.base_url, self.paths[path_key]))
        elif path:
            if self.is_blacklisted(path):
                return
            else:
                res = self.browser.open('%s/%s' % (self.base_url, path))
        else:
            self.browser.open(self.base_url)
            return

        if res and res.ok:  # If response is not None and code is below 400
            self.valid_paths['guessed'].append(path or self.paths[path_key]) \
                if guessed else self.valid_paths['discovered'].append(path or self.paths[path_key])

    def permute(self, paths, exts):
        """
        Tries single-depth permutations of base URL and path/extension combinations

        :param paths: provided list of paths
        :param exts: provided list of extensions
        :return: None
        """
        for path in paths:  # Iterate through paths
            for ext in exts:  # Iterate through extensions
                self.navigate_and_save('%s.%s' % (path, ext), guessed=True)

    def set_security(self, level):
        """
        Sets the security level for DVWA

        :param level: security level
        :return: None
        """
        self.browser.select_form()
        self.browser['security'] = level
        self.browser.submit_selected()

    def test_pages(self):
        # TODO: Docstrings
        self.find_links()

        for path in self.valid_paths['guessed'] + self.valid_paths['discovered']:
            self.test_vectors('%s/%s' % (self.base_url, path))

    def test_vectors(self, url):
        # TODO: Docstrings
        for vector in self.vectors:
            try:
                self.browser.open(url, timeout=self.timeout)
                input_fields = [field for field in self.browser.get_current_page().find_all('input')
                                if 'name' in field.attrs and field['type'] == 'text']

                if len(input_fields) == 0:
                    continue

                self.browser.select_form()

                for field in input_fields:
                    self.browser[field['name']] = vector

                res = self.browser.submit_selected()

                # Status code translation
                res_status = 'Status Code %d - %s' % (res.status_code, res.reason)

                # Find leaked sensitive data
                leaked_data = self.contains_sensitive_data(res.text)

                # Find un-sanitized data
                dirty_data = self.contains_dirty_data(res.text)

                self.test_results[url] = TEST_RESULTS(code=res.status_code,
                                                      status=res_status,
                                                      leaked=leaked_data,
                                                      dirty=dirty_data,
                                                      timeout=False)

            except Timeout:
                self.test_results[url] = TEST_RESULTS(code=None, status=None, leaked=None, dirty=None, timeout=True)
                print('Timeout exceeded on page: %s' % url)
