from distutils.core import setup
import glob
import os
import py2exe
import shutil

#shutil.rmtree("build", ignore_errors=True)
#shutil.rmtree("dist", ignore_errors=True)

py2exe_options = {
    "compressed": 2,
    "optimize": 2,
    "bundle_files": 3,
    "excludes": [
        "_gtkagg",
        "_tkagg",
        "bsddb",
        "curses",
        "email",
        "pywin.debugger",
        "pywin.debugger.dbgcon",
        "pywin.dialogs",
        "tcl",
        "Tkconstants",
        "Tkinter"
    ],
    "dll_excludes": [
        "w9xpopen.exe", # for Windows 95/98, I will not need it.
        "libgdk-win32-2.0-0.dll",
        "libgobject-2.0-0.dll",
        "tcl84.dll",
        "tk84.dll",
        "MSVCP90.dll",
        "mswsock.dll",
        "powrprof.dll",
        "api-ms-win-core-atoms-l1-1-0.dll",
        "api-ms-win-core-com-midlproxystub-l1-1-0.dll",
        "api-ms-win-core-debug-l1-1-0.dll",
        "api-ms-win-core-delayload-l1-1-0.dll",
        "api-ms-win-core-delayload-l1-1-1.dll",
        "api-ms-win-core-errorhandling-l1-1-0.dll",
        "api-ms-win-core-handle-l1-1-0.dll",
        "api-ms-win-core-heap-l2-1-0.dll",
        "api-ms-win-core-heap-obsolete-l1-1-0.dll",
        "api-ms-win-core-interlocked-l1-1-0.dll",
        "api-ms-win-core-libraryloader-l1-2-0.dll",
        "api-ms-win-core-libraryloader-l1-2-1.dll",
        "api-ms-win-core-localization-l1-2-0.dll",
        "api-ms-win-core-memory-l1-1-0.dll",
        "api-ms-win-core-processthreads-l1-1-0.dll",
        "api-ms-win-core-processthreads-l1-1-1.dll",
        "api-ms-win-core-profile-l1-1-0.dll",
        "api-ms-win-core-psapi-l1-1-0.dll",
        "api-ms-win-core-registry-l1-1-0.dll",
        "api-ms-win-core-string-l1-1-0.dll",
        "api-ms-win-core-string-l2-1-0.dll",
        "api-ms-win-core-string-obsolete-l1-1-0.dll",
        "api-ms-win-core-synch-l1-1-0.dll",
        "api-ms-win-core-synch-l1-2-0.dll",
        "api-ms-win-core-sysinfo-l1-1-0.dll",
        "api-ms-win-core-threadpool-legacy-l1-1-0.dll",
        "api-ms-win-crt-private-l1-1-0.dll",
        "api-ms-win-crt-runtime-l1-1-0.dll",
        "api-ms-win-crt-string-l1-1-0.dll",
        "api-ms-win-security-base-l1-1-0.dll"
    ]
}

setup(options={"py2exe": py2exe_options},
      zipfile=None,
      windows=[{"script": "gui.py"}])