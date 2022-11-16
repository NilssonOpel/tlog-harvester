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
_my_input_default = 'cmds.json'
_my_output_default = 'invocations.json'
_my_exe_default = 'D:/wrk/clangberget/scripts/t7.py'

DESCRIPTION = """
Make commandlines from tlogs.json input
"""
USAGE_EXAMPLE = f"""
Examples:
> {_my_name} -i {_my_input_default} -o {_my_output_default}

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
    add('-e', '--executable', metavar='THE APP',
        default=_my_exe_default,
        help='called executable')

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
def process_tlogcmds(json_file, app):
    content = open_as_json(json_file)
    argument_lines = []
    for invocation in content:
        for source_file in invocation.keys():
            argument_line = f'{app} --source_file {source_file}'
            args = invocation[source_file]
            for define in args['defines']:
                argument_line += f' -D{define}'
            for include in args['includes']:
                argument_line += f' --include {include}'
            out_dir = args.get('out_dir')
            if out_dir:
                argument_line += f' --out_dir {out_dir}'
            argument_lines.append(argument_line)

    return argument_lines

#-------------------------------------------------------------------------------
def main(options):
    ret_val = 0

    infile = options.input
    caller = options.executable

    results = process_tlogcmds(infile, caller)
    if not results:
        print(f'No input found')
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
