#!/usr/bin/env python3
#
#----------------------------------------------------------------------

import argparse
import json
import os
from   pathlib import Path
import sys
import textwrap

_my_name = os.path.basename(__file__)
_my_output_default = 'tlogs.json'

_my_ALL_glob_pattern = '*.tlog'
_my_CL_glob_pattern = 'CL.command*.tlog'

DESCRIPTION = """
Get commandlines from Visual Studio .tlog files
"""
USAGE_EXAMPLE = f"""
Examples:
> {_my_name} -d build_dir -f Release

"""

#-------------------------------------------------------------------------------
def get_my_arg_parser():
    parser = argparse.ArgumentParser(_my_name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(DESCRIPTION),
        epilog=textwrap.dedent(USAGE_EXAMPLE))
#    group = parser.add_mutually_exclusive_group()
#    group.add_argument('-r', '--replace', action='store_true',
#        help='replace all translations')
#    group.add_argument('-f', '--fill', action='store_true',
#        help='insert only the missing translations')

    add = parser.add_argument
    add('-q', '--quiet', action='store_true',
        help='be more quiet')
    add('-v', '--verbose', action='store_true',
        help='be more verbose')
    add('-d', '--directory', metavar='SEARCH-DIR',
        default=os.getcwd(),
        help='search dir')
    add('-f', '--filter', metavar='FILTER',
        help='filter on globbed files, e.g. Release or Debug')
    add('-p', '--pattern', metavar='FILE-PATTERN',
        default=_my_CL_glob_pattern,
        help='file pattern to search for')
    add('-o', '--output', metavar='OUTFILE',
        default=_my_output_default,
        help='output file (.po or .pot) with results')

    return parser

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def save_as_json(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, indent=2, ensure_ascii=False)

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def open_as_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as json_file:
        content = json.load(json_file)

    return content

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
def has_valid_text(the_string):
    if the_string.isspace():
        return False
    if len(the_string):
        return True
    return False


#-------------------------------------------------------------------------------
def glob_pattern_files(in_dir, pattern):
    the_dir = Path(in_dir)
#   print(f'Looking in {the_dir}')
    glob_files = []
    for file in the_dir.rglob(pattern):
        glob_files.append(str(file.resolve()))
    return glob_files

#-------------------------------------------------------------------------------
def filter_pattern_files(globbed_files, filter):
    filtered_files = []
    for file in globbed_files:
        if filter in file:
            filtered_files.append(file)
    return filtered_files

#-------------------------------------------------------------------------------
def parse_one_tlog_file(tlog_file):
    tested_encoding = 'utf-16le'
    with open(tlog_file, mode='r', encoding=tested_encoding) as examed_file:
        lines = examed_file.readlines()

    commands = []
    # Skip first line - it starts with a BOM so the startswith do not work
    for line in lines[1:]:
        if line.startswith('^'):
            continue
        commands.append(line)

    return commands

#-------------------------------------------------------------------------------
def parse_tlog_files(globbed_files):
    command_lines = {}
    for file in globbed_files:
        print(f'{file = }')
        tlog_output = parse_one_tlog_file(file)
        command_lines[file] = tlog_output

    return command_lines

#-------------------------------------------------------------------------------
def main():
    parser = get_my_arg_parser()
    options = parser.parse_args()
    search_dir = options.directory
    if not os.path.exists(search_dir):
        print(f'Input directory {search_dir} not found')
        parser.print_help()
        sys.exit(3)

    ret_val = 0

    glob_pattern = options.pattern
    tlogs = glob_pattern_files(search_dir, glob_pattern)

    if not tlogs:
        print(f'Found no files matching {glob_pattern} in {search_dir}')
        return 1

    if options.filter:
        tlogs = filter_pattern_files(tlogs, options.filter)

    if not tlogs:
        print(f'No files left after filter on {options.filter}')
        return 1

    results = parse_tlog_files(tlogs)
    if not results:
        print(f'No logs found')
        return 1

    result_file = options.output
    save_as_json(result_file, results)
    print(f'Results saved in {result_file}')

    return ret_val

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main())
