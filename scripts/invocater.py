#!/usr/bin/env python3
#
#----------------------------------------------------------------------

import argparse
import json
import os
from   pathlib import Path
import re
import subprocess
import sys
import textwrap

_my_name = os.path.basename(__file__)
_my_input_default = 'invocations.json'
_my_output_default = 'outputs.txt'

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

    options = parser.parse_args()
    if not os.path.exists(options.input):
        print(f'Input file {options.input} not found')
        parser.print_help()
        sys.exit(3)
    return options

#-------------------------------------------------------------------------------
def ccp():
    '''Get current code page'''
    try:
        return ccp.codepage
    except AttributeError:
        reply = os.popen('cmd /c CHCP').read()
        cp = re.match(r'^.*:\s+(\d*)$', reply)
        if cp:
            ccp.codepage = cp.group(1)
        else:
            ccp.codepage = 'utf-8'
        return ccp.codepage

#-------------------------------------------------------------------------------
def run_process(command, do_check, extra_dir=os.getcwd(), as_text=True):
    exit_code = 0
    try:
        encoding_used = None
        if as_text:
            encoding_used = ccp()

        status = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=as_text,
                                shell=True,
                                encoding=encoding_used,  # See https://bugs.python.org/issue27179
                                check=do_check)
        if status.returncode == 0:
            reply = status.stdout
        else:
            reply = status.stdout
            reply += status.stderr
        exit_code = status.returncode

    except Exception as e:
        reply = '\n-start of exception-\n'
        reply += f'The command\n>{command}\nthrew an exception'
        if extra_dir:
            reply += f' (standing in directory {extra_dir})'
        reply += f':\n\n'
        reply += f'type:  {type(e)}\n'
        reply += f'text:  {e}\n'
        reply += '\n-end of exception-\n'
        reply += f'stdout: {e.stdout}\n'
        reply += f'stderr: {e.stderr}\n'
        if as_text == False:
            reply = reply.encode('utf-8')
        exit_code = 3

    return reply, exit_code

#-------------------------------------------------------------------------------
def save_as_json(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, indent=2, ensure_ascii=False)

#-------------------------------------------------------------------------------
def open_as_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as json_file:
        content = json.load(json_file)

    return content
#
'''
        command = 'git pull'
        reply, exit_code = run_process(command, True, git_dir)

'''
#-------------------------------------------------------------------------------
def process_cmds(invocation_file, options):
    content = open_as_json(invocation_file)
    output_lines = []
    for invocation in content:
        if options.verbose:
            print(f'python {invocation}')
        reply, exit_code = run_process(invocation, True)
        output_lines.append(reply)
    return output_lines

#-------------------------------------------------------------------------------
def main(options):
    ret_val = 0

    infile = options.input

    results = process_cmds(infile, options)
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
