#!/usr/bin/env python
# coding:utf-8
#
# xiaoyu <xiaokong1937@gmail.com>
#
# 2014/12/25
#
"""
Command.

"""
import logging
from optparse import make_option, OptionParser
import sys

logger = logging.getLogger("root")
formatter = logging.Formatter(
    "%(name)s - %(asctime)s - %(levelname)s :%(message)s",
    "%a, %d %b %Y %H:%M:%S",)
file_handler = logging.FileHandler("xlink.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


class BaseCommand(object):
    option_list = (
        make_option('-v', '--verbosity', action='store', dest='verbosity',
                    default='1', type='choice', choices=['0', '1', '2']),
    )
    help = ''
    args = ''

    def get_version(self):
        return '1.0.1'

    def usage(self, subcommand):
        """
        Return a brief description of how to use this command, by
        default from the attribute ``self.help``.

        """
        usage = '%%prog {} [options] {}'.format(subcommand, self.args)
        if self.help:
            return '{}\n\n{}'.format(usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand):
        """
        Create and return the ``OptionParser`` which will be used to
        parse the arguments to this command.

        """
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            version=self.get_version(),
                            option_list=self.option_list)

    def print_help(self, prog_name, subcommand):
        """
        Print the help message for this command, derived from
        ``self.usage``.

        """
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        parser = self.create_parser(argv[0], argv[1])
        options, args = parser.parse_args(argv[2:])
        try:
            self.execute(*args, **options.__dict__)
        except Exception as e:
            print e
            sys.exit(1)

    def execute(self, *args, **options):
        raise NotImplementedError()
