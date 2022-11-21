setlocal
..\scripts\tlog-harvester.py -d %1 -f Release
..\scripts\tlog2cmd.py
..\scripts\cmds2ninja.py -i cmds.json -v --executable %2



