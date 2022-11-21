setlocal
set PY_BUILD=D:\wrk\python-src\cpython\PCbuild\obj\312amd64_Release
set EXEC="python ..\..\clangberget\scripts\t7.py"
call test.bat %PY_BUILD% %EXEC%
ninja
