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
_my_output_default = 'build.ninja'
_my_exe_default = 'D:/wrk/clangberget/scripts/t7.py'

DESCRIPTION = f"""
Make ninja file from {_my_input_default} input
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
def open_as_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as json_file:
        content = json.load(json_file)

    return content

#-------------------------------------------------------------------------------
def ninja_escape(instring):
    outstring = ""

    instring = instring.strip()

    index = 0
    while index < len(instring):
        ch = instring[index]
        index += 1
        if ch == '"':
            if (index+1 < len(instring)) and (instring[index] == ' '):
                outstring += ' '
                index += 1
            continue
        elif ch == ' ':
            outstring += "$ "
        elif ch == ':':
            outstring += "$:"
        elif ch == '$':
            outstring += "$$"
        else:
            outstring += ch
#    print("IN: "+instring)
#    print("UT: "+outstring)

    return outstring

#-------------------------------------------------------------------------------
def generate_ninja_file(json_input, compiler_tool, ninja_file, options):
    print("I am in generate_ninja_file")

    f = open(ninja_file, "w")
    f.write("ninja_required_version=1.3\n\n")
    f.write("rule COMPILE\n")
    f.write("  depfile = $out.d\n")
    f.write("  deps = gcc\n")
    f.write("  command = $CMDLINE --dependency $out.d\n\n")

    for invocation in json_input:
        for src_file in invocation.keys():
            out_file = os.path.basename(src_file) + '.indx'
            argument_line = f'{compiler_tool} --source_file {src_file}'
            args = invocation[src_file]

            for define in args['defines']:
                argument_line += f' -D{define}'
            for include in args['includes']:
                argument_line += f' --include {include}'

            out_dir = args.get('out_dir')
            if out_dir:
                out_file = os.path.join(out_dir, out_file)
            argument_line += f' --output_file {out_file}'

            out_file = ninja_escape(out_file)
            src_file = ninja_escape(src_file)
            f.write("build " + out_file + ": COMPILE " + src_file + "\n")

            argument_line = ninja_escape(argument_line)
            f.write("  CMDLINE=" + argument_line)
            f.write("\n\n")

    f.close()

    return ninja_file

#-------------------------------------------------------------------------------
def main(options):
    ret_val = 0

    infile = options.input
    json_input = open_as_json(infile)
    calling_tool = options.executable
    ninja_file = options.output

    ninja_file = generate_ninja_file(json_input, calling_tool, ninja_file, options)

    print(f'Results saved in {ninja_file}')

    return ret_val

#-------------------------------------------------------------------------------
#
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(parse_arguments()))
