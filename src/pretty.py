"""
:author: Henry Larson
:description: class to pretty print collected data from scraping operations
"""

from urllib import parse

DISCOVER_HEADER = '------DISCOVER------'
TEST_HEADER = '--------TEST--------'
SEP = '===================='


class FuzzPrinter:
    def __init__(self):
        pass

    @staticmethod
    def prettify_discovered_data(base_url, discovered_pages, discovered_inputs):
        """
        Pretty prints the data retrieved from 'discovery' operations

        :return: None
        """
        # Print header
        print(DISCOVER_HEADER)

        # Guessed pages parsing
        print('Links Found on Page:\n%s' % SEP)
        for path in discovered_pages.paths['discovered']:
            print(parse.urljoin(base_url, path))

        # Discovered pages parsing
        print('\nLinks Successfully Guessed:\n%s' % SEP)
        for path in discovered_pages.paths['guessed']:
            print(parse.urljoin(base_url, path))

        # Discovered inputs parsing
        print('\nInput Forms on Pages\n%s' % SEP)
        for path, inputs in discovered_inputs.fields.items():
            print(path)
            [print('\t%s' % field['name']) for field in inputs]

        # Cookies parsing
        print('\nCookies\n%s' % SEP)
        [print(cookie) for cookie in discovered_inputs.cookies]

    @staticmethod
    def prettify_tested_data(results: dict):
        # TODO: Docstrings
        # Print header
        print(TEST_HEADER)

        dirty_data_count = 0
        leaked_data_count = 0
        dos_vulnerabilities = 0
        http_errors = 0

        for url, result in results.items():
            dirty_data_count += len(result.dirty) if result.dirty else 0
            leaked_data_count += len(result.leaked) if result.leaked else 0
            dos_vulnerabilities += 1 if result.timeout else 0
            http_errors += 1 if result.code and result.code >= 400 else 0

            print('Page URL: %s' % url)
            print('Status: %s\nLeaked Data: %s\nUn-sanitized Data: %s\n' %
                  (result.status, ', '.join(result.leaked), ', '.join(result.dirty))
                  if not result.timeout else 'Page timed out\n')

        print('Results:\n%s\nUn-sanitized Inputs: %d\nSensitive Data Leakages: %d\nDOS Vulnerabilities: %d'
              '\nResponse Code Errors: %d' % (SEP,
                                              dirty_data_count,
                                              leaked_data_count,
                                              dos_vulnerabilities,
                                              http_errors))
