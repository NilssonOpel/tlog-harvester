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
_my_input_default = 'tlogs.json'
_my_output_default = 'cmds.json'


DESCRIPTION = """
Make commandlines from tlogs.json input
"""
USAGE_EXAMPLE = f"""
Examples:
> {_my_name} -i tlog.json -o cmdlines.json

"""

#-------------------------------------------------------------------------------
def parse_arguments():
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
    add('-i', '--input', metavar='INFILE',
        default=_my_input_default,
        help='input file (.json)')
    add('-o', '--output', metavar='OUTFILE',
        default=_my_output_default,
        help='output file')

    options = parser.parse_args()
    if not os.path.exists(options.input):
        print(f'Input file {options.input} not found')
        parser.print_help()
        sys.exit(3)
    return options

#-------------------------------------------------------------------------------
def save_as_json(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, indent=2, ensure_ascii=False)

#-------------------------------------------------------------------------------
def open_as_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as json_file:
        content = json.load(json_file)

    return content

#-------------------------------------------------------------------------------
def eat_ws(cmd_line, curr_index, stop_index):
    curr_char = cmd_line[curr_index]
    while curr_char.isspace() and curr_index < stop_index:
        curr_index += 1
        curr_char = cmd_line[curr_index]

    return curr_index

#-------------------------------------------------------------------------------
def eat_until_ws(cmd_line, curr_index, stop_index):
    curr_char = cmd_line[curr_index]
    while not curr_char.isspace() and curr_index < stop_index:
        curr_index += 1
    return curr_index

#-------------------------------------------------------------------------------
def extract_from_pattern(cmd_line, pattern):
    extracts = []
    curr_index = 0
    stop_index = len(cmd_line)
    pattern_len = len(pattern)
    while curr_index < stop_index:
#        print(f'START {curr_index} : {stop_index}')
        # find the start
        curr_index = cmd_line.find(pattern, curr_index, stop_index)
#        print(f'  FIND {curr_index}')
        if curr_index == -1:
            break
        curr_index += pattern_len
        curr_index = eat_ws(cmd_line, curr_index, stop_index)
        end_index = cmd_line.find(' ', curr_index, stop_index)
        if end_index == -1:
            end_index = stop_index
        the_extract = cmd_line[curr_index:end_index]
        extracts.append(the_extract)
#        print(f' {curr_index} : {end_index}')
#        print(f'{the_extract =}')
        curr_index = end_index
    return extracts

#-------------------------------------------------------------------------------
def handle_defines(cmd_line):
    defines = []
    curr_index = 0
    stop_index = len(cmd_line)
    while curr_index < stop_index:
        print(f'DEFINES {curr_index} : {stop_index}')
        # find the start
        curr_index = cmd_line.find(' /D', curr_index, stop_index)
        print(f'  FIND {curr_index}')
        if curr_index == -1:
            break
        curr_index += 3
        curr_index = eat_ws(cmd_line, curr_index, stop_index)
        end_index = cmd_line.find(' ', curr_index, stop_index)
        if end_index == -1:
            end_index = stop_index
        the_define = cmd_line[curr_index:end_index]
        defines.append(the_define)
        print(f' {curr_index} : {end_index}')
        print(f'{the_define =}')
        curr_index = end_index
    return defines

#-------------------------------------------------------------------------------
def handle_includes(cmd_line):
    defines = []
    curr_index = 0
    stop_index = len(cmd_line)
    while curr_index < stop_index:
        print(f'INCLUDES {curr_index} : {stop_index}')
        # find the start
        curr_index = cmd_line.find(' /I', curr_index, stop_index)
        if curr_index == -1:
            break
        curr_index += 3
        curr_index = eat_ws(cmd_line, curr_index, stop_index)
        end_index = cmd_line.find(' ', curr_index, stop_index)
        if end_index == -1:
            end_index = stop_index
        the_include = cmd_line[curr_index:end_index]
        defines.append(the_include)
        print(f'{the_include =}')
        curr_index = end_index
    return defines

#-------------------------------------------------------------------------------
def extract_source_file(cmd_line):
    source_file_name = ""
    curr_index = 0
    stop_index = len(cmd_line)
    # First skip the \n" ending
    end_index = cmd_line.rfind('\n"', 0, stop_index)
    start_index = cmd_line.rfind(' ', 0, end_index)

    source_file_name = cmd_line[start_index:end_index]
    print(f'{source_file_name =}')

    return source_file_name

#-------------------------------------------------------------------------------
def process_line(cmd_line):
    commands = {}
    content = {}
    defines = extract_from_pattern(cmd_line, ' /D')
    includes = extract_from_pattern(cmd_line, ' /I')
    source_file = extract_source_file(cmd_line)
    content['defines'] = defines
    content['includes'] = includes
    commands[source_file] = content
    return commands

#-------------------------------------------------------------------------------
def process_tlogs(json_file):
    content = open_as_json(json_file)
    command_lines = []
    for tlog_dir in content.keys():
        print(f'{tlog_dir = }')
        cmd_list = content[tlog_dir]
        for cmd_line in cmd_list:
            print(f'{cmd_line = }')
            results = process_line(cmd_line)
            command_lines.append(results)

    return command_lines

#-------------------------------------------------------------------------------
def main(options):
    ret_val = 0

    infile = options.input

    results = process_tlogs(infile)
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
    sys.exit(main(parse_arguments()))
