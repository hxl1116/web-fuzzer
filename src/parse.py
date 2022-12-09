"""
:author: Henry Larson
:description: parser class for command line argument parsing operations
"""

from argparse import ArgumentParser

# Help messages (positionals)
DISCOVER_HELP_MSG = 'Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques ' \
                    'include both crawling and guessing.'
TEST_HELP_MSG = 'Discover all inputs, then attempt a list of exploit vectors on those inputs. Report anomalies that ' \
                'could be vulnerabilities.'

# Help messages (optionals)
COMMON_WORDS_HELP_MSG = 'Newline-delimited file of common words to be used in page guessing. Required.'
EXTENSIONS_HELP_MSG = 'Newline-delimited file of path extensions, e.g. ".php". Optional. Defaults to ".php" and the ' \
                      'empty string if not specified'
CUSTOM_AUTH_HELP_MSG = 'Signal that the fuzzer should use hard-coded authentication for a specific application ' \
                       '(e.g. dvwa).'
VECTORS_HELP_MSG = 'Newline-delimited file of common exploits to vulnerabilities. Required.'
SANITIZED_HELP_MSG = 'Newline-delimited file of characters that should be sanitized from inputs. Defaults to just ' \
                     '\'<\' and \'>\''
SENSITIVE_HELP_MSG = 'Newline-delimited file data that should never be leaked. It\'s assumed that this data is in ' \
                     'the application\'s database (e.g. test data), but is not reported in any response. Required.'
SLOW_HELP_MSG = 'Number of milliseconds considered when a response is considered "slow". Optional. Default is 500 ' \
                'milliseconds'


class FuzzParser:
    """
    Class used to parse command line arguments
    """
    parser = ArgumentParser(prog='fuzz', usage='%(prog)s [discover | test] URL [--custom-auth AUTH]',
                            description='Web Fuzzer CLI')

    def __init__(self):
        """
        Initializes command groups with positionals and optionals
        """
        # Main parser optionals
        self.parser.add_argument('--version', action='version', version='%(prog)s 1.0')

        # Subparser configuration
        subparsers = self.parser.add_subparsers(title='modes', dest='mode',
                                                help='\'discover\' or \'test\' modes', metavar='discover | test')
        self.discover_parser = subparsers.add_parser('discover')
        self.test_parser = subparsers.add_parser('test')

        # Discover group positionals and optionals
        self.discover_parser.add_argument('destination', nargs=1, type=str, help=DISCOVER_HELP_MSG)
        self.discover_parser.add_argument('--custom-auth', nargs=1, default='', type=str, help=CUSTOM_AUTH_HELP_MSG,
                                          dest='auth')
        self.discover_parser.add_argument('--common-words', nargs=1, type=str, help=COMMON_WORDS_HELP_MSG, dest='words')
        self.discover_parser.add_argument('--extensions', nargs=1, default='php', type=str, help=EXTENSIONS_HELP_MSG,
                                          dest='exts')

        # Test group positionals and optionals
        self.test_parser.add_argument('destination', nargs=1, type=str, help=TEST_HELP_MSG)
        self.test_parser.add_argument('--custom-auth', nargs=1, default='', type=str, help=CUSTOM_AUTH_HELP_MSG,
                                      dest='auth')
        self.test_parser.add_argument('--common-words', nargs=1, type=str, help=COMMON_WORDS_HELP_MSG, dest='words')
        self.test_parser.add_argument('--extensions', nargs=1, default='php', type=str, help=EXTENSIONS_HELP_MSG,
                                      dest='exts')
        self.test_parser.add_argument('--vectors', nargs=1, type=str, help=VECTORS_HELP_MSG, dest='vectors')
        self.test_parser.add_argument('--sanitized-chars', nargs=1, default=['<', '>'], type=str,
                                      help=SANITIZED_HELP_MSG, dest='sanitize')
        self.test_parser.add_argument('--sensitive', nargs=1, type=str, help=SENSITIVE_HELP_MSG, dest='sensitive')
        self.test_parser.add_argument('--slow', nargs=1, default=.5, type=int, help=SLOW_HELP_MSG, dest='timeout')

    def parse(self, args):
        """
        Removes the 'discover' or 'test' string from the command line arguments

        :param args: the command line arguments
        :return: arguments consumed by the parser
        """

        return self.parser.parse_args(args)

    def usage(self):
        """
        Prints the usage message for the application

        :return: None
        """
        self.parser.print_usage()

    def help(self):
        """
        Prints the help message for the application

        :return: None
        """
        self.parser.print_help()
