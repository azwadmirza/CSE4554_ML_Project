    def _create_batch_scripts(self):
        """Create batch scripts"""
        self._print("Creating batch scripts")
        self.create_batch_script('readme.txt',
r"""These batch files are required to run WinPython icons.

These files should help the user writing his/her own
specific batch file to call Python scripts inside WinPython.
The environment variables are set-up in 'env_.bat' and 'env_for_icons.bat'.""")
        conv = lambda path: ";".join(['%WINPYDIR%\\'+pth for pth in path])
        path = conv(self.prepath) + ";%PATH%;" + conv(self.postpath)


        self.create_batch_script('make_cython_use_mingw.bat', r"""@echo off
call %~dp0env.bat

rem ******************
rem mingw part
rem ******************

set pydistutils_cfg=%WINPYDIR%\..\settings\pydistutils.cfg

set tmp_blank=
echo [config]>"%pydistutils_cfg%"
echo compiler=mingw32>>"%pydistutils_cfg%"

echo [build]>>"%pydistutils_cfg%"
echo compiler=mingw32>>"%pydistutils_cfg%"

echo [build_ext]>>"%pydistutils_cfg%"
echo compiler=mingw32>>"%pydistutils_cfg%"

echo cython has been set to use mingw32
echo to remove this, remove file "%pydistutils_cfg%"

rem pause

""")

        self.create_batch_script('make_cython_use_vc.bat', r"""@echo off
call %~dp0env.bat
set pydistutils_cfg=%WINPYDIR%\..\settings\pydistutils.cfg
echo [config]>%pydistutils_cfg%
        """)

        self.create_batch_script('make_winpython_movable.bat',r"""@echo off
call %~dp0env.bat
echo patch pip and current launchers for move

%WINPYDIR%\python.exe -c "from winpython import wppm;dist=wppm.Distribution(r'%WINPYDIR%');dist.patch_standard_packages('pip', to_movable=True)"
pause
        """)

        self.create_batch_script('make_winpython_fix.bat',r"""@echo off
call %~dp0env.bat
echo patch pip and current launchers for non-move

%WINPYDIR%\python.exe -c "from winpython import wppm;dist=wppm.Distribution(r'%WINPYDIR%');dist.patch_standard_packages('pip', to_movable=False)"
pause
        """)

        self.create_batch_script('make_working_directory_be_not_winpython.bat', r"""@echo off
set winpython_ini=%~dp0..\\settings\winpython.ini
echo [debug]>"%winpython_ini%"
echo state = disabled>>"%winpython_ini%"
echo [environment]>>"%winpython_ini%"
echo ## <?> Uncomment lines to override environment variables>>"%winpython_ini%"
echo HOME = %%HOMEDRIVE%%%%HOMEPATH%%\Documents\WinPython%%WINPYVER%%\settings>>"%winpython_ini%"
echo JUPYTER_DATA_DIR = %%HOME%%>>"%winpython_ini%"
echo WINPYWORKDIR = %%HOMEDRIVE%%%%HOMEPATH%%\Documents\WinPython%%WINPYVER%%\Notebooks>>"%winpython_ini%"
""")

        self.create_batch_script('make_working_directory_be_winpython.bat', r"""@echo off
set winpython_ini=%~dp0..\\settings\winpython.ini
echo [debug]>"%winpython_ini%"
echo state = disabled>>"%winpython_ini%"
echo [environment]>>"%winpython_ini%"
echo ## <?> Uncomment lines to override environment variables>>"%winpython_ini%"
echo #HOME = %%HOMEDRIVE%%%%HOMEPATH%%\Documents\WinPython%%WINPYVER%%\settings>>"%winpython_ini%"
echo #JUPYTER_DATA_DIR = %%HOME%%>>"%winpython_ini%"
echo #WINPYWORKDIR = %%HOMEDRIVE%%%%HOMEPATH%%\Documents\WinPython%%WINPYVER%%\Notebooks>>"%winpython_ini%"
""")

        self.create_batch_script('cmd.bat', r"""@echo off
call "%~dp0env_for_icons.bat"
cmd.exe /k""")
        self.create_batch_script('python.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
rem backward compatibility for  python command-line users
"%WINPYDIR%\python.exe"  %*
""")                
        self.create_batch_script('winpython.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
rem backward compatibility for non-ptpython users
if exist "%WINPYDIR%\scripts\ptpython.exe" (
    "%WINPYDIR%\scripts\ptpython.exe" %*
) else (
    "%WINPYDIR%\python.exe"  %*
)
""")                

        self.create_batch_script('idlex.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
rem backward compatibility for non-IDLEX users
if exist "%WINPYDIR%\scripts\idlex.pyw" (
    "%WINPYDIR%\python.exe" "%WINPYDIR%\scripts\idlex.pyw" %*
) else (
    "%WINPYDIR%\python.exe" "%WINPYDIR%\Lib\idlelib\idle.pyw" %*
)
""")

        self.create_batch_script('spyder.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
"%WINPYDIR%\scripts\spyder.exe" %*
""")

        self.create_batch_script('spyder_reset.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
%WINPYDIR%\scripts\spyder.exe --reset %*
""")

        self.create_batch_script('ipython_notebook.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
"%WINPYDIR%\scripts\jupyter-notebook.exe" %*
""")

        self.create_batch_script('qtconsole.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
"%WINPYDIR%\scripts\jupyter-qtconsole.exe" %*
""")
 
        self.create_batch_script('qtdemo.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
if "%QT_API%"=="pyqt5" (
    "%WINPYDIR%\python.exe" "%WINPYDIR%\Lib\site-packages\PyQt5\examples\qtdemo\demo.py"
) else (
    "%WINPYDIR%\pythonw.exe" "%WINPYDIR%\Lib\site-packages\PyQt4\examples\demos\qtdemo\qtdemo.pyw"
)
""")

        self.create_batch_script('qtdesigner.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
if "%QT_API%"=="pyqt5" (
    "%WINPYDIR%\Lib\site-packages\PyQt5\designer.exe" %*
) else (
    "%WINPYDIR%\Lib\site-packages\PyQt4\designer.exe" %*
)
""")

        self.create_batch_script('qtassistant.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
if "%QT_API%"=="pyqt5" (
    "%WINPYDIR%\Lib\site-packages\PyQt5\assistant.exe" %*
) else (
    "%WINPYDIR%\Lib\site-packages\PyQt4\assistant.exe" %*
)
""")        

        self.create_batch_script('qtlinguist.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
if "%QT_API%"=="pyqt5" (
    cd/D "%WINPYDIR%\Lib\site-packages\PyQt5"
    "%WINPYDIR%\Lib\site-packages\PyQt5\linguist.exe" %*
) else (
    cd/D "%WINPYDIR%\Lib\site-packages\PyQt4"
    "%WINPYDIR%\Lib\site-packages\PyQt4\linguist.exe" %*
)
""")        
        
        self.create_python_batch('register_python.bat', 'register_python',
                                 workdir=r'"%WINPYDIR%\Scripts"')
        self.create_batch_script('register_python_for_all.bat',
                                 r"""@echo off
call %~dp0env.bat
call %~dp0register_python.bat --all""")

        self.create_batch_script('wpcp.bat',r"""@echo off
call "%~dp0env_for_icons.bat"
cd/D "%WINPYWORKDIR%"
%WINPYDIR%\python.exe -m winpython.controlpanel %*
""")

        #self.create_python_batch('wpcp.bat', '-m winpython.controlpanel',
        #                         workdir=r'"%WINPYDIR%\Scripts"')

        self.create_batch_script('upgrade_pip.bat', r"""@echo off
call %~dp0env.bat
echo this will upgrade pip with latest version, then patch it for WinPython portability ok ?
pause
%WINPYDIR%\python.exe -m pip install --upgrade --force-reinstall  pip
%WINPYDIR%\python.exe -c "from winpython import wppm;dist=wppm.Distribution(r'%WINPYDIR%');dist.patch_standard_packages('pip', to_movable=True)
pause
""")

        # pre-run mingw batch
        print('now pre-running extra mingw')
        filepath = osp.join(self.winpydir, 'scripts', 'make_cython_use_mingw.bat')
        p = subprocess.Popen(filepath, shell=True, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()

        self._print_done()