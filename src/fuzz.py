"""
:author: Henry Larson
:description: main file to run fuzzing operations
"""
from auth import get_auth
from scrape import FuzzScraper
from parse import FuzzParser
from pretty import FuzzPrinter

import sys


def get_file_data(arg):
    """
    Reads all data from a provided file

    :param arg: argument default or filename
    :return: parsed file data
    """
    try:
        with open(arg[0], 'r') as file:
            data = [line.strip() for line in file if not str(line).__contains__("#")]
            file.close()

            return data
    except FileNotFoundError:
        return arg


def set_security_level(args, level):
    """
    Utilizes the custom built scraper to set the DVWA security level

    :param args: command line arguments
    :param level: security level
    :return: None
    """
    [username, password] = get_auth(args.auth[0])

    scraper.login({'username': username, 'password': password})
    scraper.navigate_and_save(path_key='sec')
    scraper.set_security(level)


def handle_args(args, sec_lvl='Low'):
    """
    Handles arguments passed in via optionals before delegating to 'discover' or 'test' specific functions

    :return: None
    """
    if args.auth:
        set_security_level(args, sec_lvl)
    else:
        scraper.navigate()

    if args.words:
        scraper.permute(get_file_data(args.words), get_file_data(args.exts))


def handle_discover(args):
    """
    Handles the execution of 'discover' command operations

    :param args: command line arguments
    :return: None
    """

    scraper.find_links()
    scraper.discover_inputs()


def handle_test(args):
    """
    Handles the execution of 'test' command operations
    :return:
    """

    if args.vectors:
        vectors = get_file_data(args.vectors)
    else:
        print('--vectors=file is a required argument.')
        exit(0)

    if args.sensitive:
        sensitive = get_file_data(args.sensitive)
    else:
        print('--sensitive=file is a required argument.')
        exit(0)

    sanitized = get_file_data(args.sanitize)

    # Set timeout
    scraper.timeout = args.timeout

    scraper.vectors = vectors
    scraper.sensitive = sensitive
    scraper.sanitized_chars = sanitized

    scraper.test_pages()


def print_discovered_data(args=None):
    # TODO: Docstrings
    printer.prettify_discovered_data(scraper.base_url, scraper.compile_pages(), scraper.compile_inputs())


def print_tested_data(args=None):
    # TODO: Docstrings
    printer.prettify_tested_data(scraper.test_results)


def main():
    """
    Prepares the command line arguments and selects the appropriate handling method

    :return: None
    """
    mode_functions = {'discover': [handle_args, handle_discover, print_discovered_data],
                      'test': [handle_args, handle_test, print_tested_data]}

    args = parser.parse(sys.argv[1:])
    scraper.base_url = args.destination[0]

    # Handle args for respective mode
    [func(args) for func in mode_functions[args.mode]]


if __name__ == '__main__':
    parser = FuzzParser()
    scraper = FuzzScraper()
    printer = FuzzPrinter()

    main()
