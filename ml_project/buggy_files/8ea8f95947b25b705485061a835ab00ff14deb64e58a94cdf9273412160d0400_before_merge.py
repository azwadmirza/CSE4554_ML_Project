def DEFAULT_VARS():
    dv = {
        "ANSICON": Var(
            is_string,
            ensure_string,
            ensure_string,
            DefaultNotGiven,
            "This is used on Windows to set the title, if available.",
            doc_configurable=False,
        ),
        "AUTO_CD": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Flag to enable changing to a directory by entering the dirname or "
            "full path only (without the cd command).",
        ),
        "AUTO_PUSHD": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Flag for automatically pushing directories onto the directory stack.",
        ),
        "AUTO_SUGGEST": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Enable automatic command suggestions based on history, like in the fish "
            "shell.\n\nPressing the right arrow key inserts the currently "
            "displayed suggestion. Only usable with ``$SHELL_TYPE=prompt_toolkit.``",
        ),
        "AUTO_SUGGEST_IN_COMPLETIONS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Places the auto-suggest result as the first option in the completions. "
            "This enables you to tab complete the auto-suggestion.",
        ),
        "ASYNC_INVALIDATE_INTERVAL": Var(
            is_float,
            float,
            str,
            0.05,
            "When ENABLE_ASYNC_PROMPT is True, it may call the redraw frequently. "
            "This is to group such calls into one that happens within that timeframe. "
            "The number is set in seconds.",
        ),
        "ASYNC_PROMPT_THREAD_WORKERS": Var(
            is_int,
            int,
            str,
            None,
            "Define the number of workers used by the ASYC_PROPMT's pool. "
            "By default it is defined by Python's concurrent.futures.ThreadPoolExecutor",
        ),
        "BASH_COMPLETIONS": Var(
            is_env_path,
            str_to_env_path,
            env_path_to_str,
            BASH_COMPLETIONS_DEFAULT,
            "This is a list (or tuple) of strings that specifies where the "
            "``bash_completion`` script may be found. "
            "The first valid path will be used. For better performance, "
            "bash-completion v2.x is recommended since it lazy-loads individual "
            "completion scripts. "
            "For both bash-completion v1.x and v2.x, paths of individual completion "
            "scripts (like ``.../completes/ssh``) do not need to be included here. "
            "The default values are platform "
            "dependent, but sane. To specify an alternate list, do so in the run "
            "control file.",
            doc_default=(
                "Normally this is:\n\n"
                "    ``('/usr/share/bash-completion/bash_completion', )``\n\n"
                "But, on Mac it is:\n\n"
                "    ``('/usr/local/share/bash-completion/bash_completion', "
                "'/usr/local/etc/bash_completion')``\n\n"
                "Other OS-specific defaults may be added in the future."
            ),
        ),
        "CASE_SENSITIVE_COMPLETIONS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            ON_LINUX,
            "Sets whether completions should be case sensitive or case " "insensitive.",
            doc_default="True on Linux, False otherwise.",
        ),
        "CDPATH": Var(
            is_env_path,
            str_to_env_path,
            env_path_to_str,
            (),
            "A list of paths to be used as roots for a cd, breaking compatibility "
            "with Bash, xonsh always prefer an existing relative path.",
        ),
        "COLOR_INPUT": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Flag for syntax highlighting interactive input.",
        ),
        "COLOR_RESULTS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Flag for syntax highlighting return values.",
        ),
        "COMPLETIONS_BRACKETS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Flag to enable/disable inclusion of square brackets and parentheses "
            "in Python attribute completions.",
            doc_default="True",
        ),
        "COMPLETIONS_CONFIRM": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "While tab-completions menu is displayed, press <Enter> to confirm "
            "completion instead of running command. This only affects the "
            "prompt-toolkit shell.",
        ),
        "COMPLETIONS_DISPLAY": Var(
            is_completions_display_value,
            to_completions_display_value,
            str,
            "multi",
            "Configure if and how Python completions are displayed by the "
            "``prompt_toolkit`` shell.\n\nThis option does not affect Bash "
            "completions, auto-suggestions, etc.\n\nChanging it at runtime will "
            "take immediate effect, so you can quickly disable and enable "
            "completions during shell sessions.\n\n"
            "- If ``$COMPLETIONS_DISPLAY`` is ``none`` or ``false``, do not display"
            " those completions.\n"
            "- If ``$COMPLETIONS_DISPLAY`` is ``single``, display completions in a\n"
            "  single column while typing.\n"
            "- If ``$COMPLETIONS_DISPLAY`` is ``multi`` or ``true``, display completions"
            " in multiple columns while typing.\n\n"
            "- If ``$COMPLETIONS_DISPLAY`` is ``readline``, display completions\n"
            "  will emulate the behavior of readline.\n\n"
            "These option values are not case- or type-sensitive, so e.g. "
            "writing ``$COMPLETIONS_DISPLAY = None`` "
            "and ``$COMPLETIONS_DISPLAY = 'none'`` are equivalent. Only usable with "
            "``$SHELL_TYPE=prompt_toolkit``",
        ),
        "COMPLETIONS_MENU_ROWS": Var(
            is_int,
            int,
            str,
            5,
            "Number of rows to reserve for tab-completions menu if "
            "``$COMPLETIONS_DISPLAY`` is ``single`` or ``multi``. This only affects the "
            "prompt-toolkit shell.",
        ),
        "COMPLETION_QUERY_LIMIT": Var(
            is_int,
            int,
            str,
            100,
            "The number of completions to display before the user is asked "
            "for confirmation.",
        ),
        "COMPLETION_IN_THREAD": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "When generating the completions takes time, "
            "it’s better to do this in a background thread. "
            "When this is True, background threads is used for completion.",
        ),
        "DIRSTACK_SIZE": Var(
            is_int, int, str, 20, "Maximum size of the directory stack."
        ),
        "DOTGLOB": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            'Globbing files with "*" or "**" will also match '
            "dotfiles, or those 'hidden' files whose names "
            "begin with a literal '.'. Such files are filtered "
            "out by default.",
        ),
        "DYNAMIC_CWD_WIDTH": Var(
            is_dynamic_cwd_width,
            to_dynamic_cwd_tuple,
            dynamic_cwd_tuple_to_str,
            (float("inf"), "c"),
            "Maximum length in number of characters "
            "or as a percentage for the ``cwd`` prompt variable. For example, "
            '"20" is a twenty character width and "10%" is ten percent of the '
            "number of columns available.",
        ),
        "DYNAMIC_CWD_ELISION_CHAR": Var(
            is_string,
            ensure_string,
            ensure_string,
            "",
            "The string used to show a shortened directory in a shortened cwd, "
            "e.g. ``'…'``.",
        ),
        "ENABLE_ASYNC_PROMPT": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "When enabled the prompt is loaded from threads making the shell faster. "
            "Sections that take long will be updated in the background. ",
        ),
        "EXPAND_ENV_VARS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Toggles whether environment variables are expanded inside of strings "
            "in subprocess mode.",
        ),
        "FORCE_POSIX_PATHS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Forces forward slashes (``/``) on Windows systems when using auto "
            "completion if set to anything truthy.",
            doc_configurable=ON_WINDOWS,
        ),
        "FOREIGN_ALIASES_SUPPRESS_SKIP_MESSAGE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not foreign aliases should suppress the message "
            "that informs the user when a foreign alias has been skipped "
            "because it already exists in xonsh.",
            doc_configurable=True,
        ),
        "FOREIGN_ALIASES_OVERRIDE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not foreign aliases should override xonsh aliases "
            "with the same name. Note that setting of this must happen in the "
            "environment that xonsh was started from. "
            "It cannot be set in the ``.xonshrc`` as loading of foreign aliases happens before"
            "``.xonshrc`` is parsed",
            doc_configurable=True,
        ),
        "FUZZY_PATH_COMPLETION": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Toggles 'fuzzy' matching of paths for tab completion, which is only "
            "used as a fallback if no other completions succeed but can be used "
            "as a way to adjust for typographical errors. If ``True``, then, e.g.,"
            " ``xonhs`` will match ``xonsh``.",
        ),
        "GLOB_SORTED": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Toggles whether globbing results are manually sorted. If ``False``, "
            "the results are returned in arbitrary order.",
        ),
        "HISTCONTROL": Var(
            is_string_set,
            csv_to_set,
            set_to_csv,
            set(),
            "A set of strings (comma-separated list in string form) of options "
            "that determine what commands are saved to the history list. By "
            "default all commands are saved. The option ``ignoredups`` will not "
            "save the command if it matches the previous command. The option "
            "``ignoreerr`` will cause any commands that fail (i.e. return non-zero "
            "exit status) to not be added to the history list. The option "
            "``erasedups`` will remove all previous commands that matches and updates the frequency. "
            "Note: ``erasedups`` is supported only in sqlite backend).",
            doc_store_as_str=True,
        ),
        "HOSTNAME": Var(
            is_string,
            ensure_string,
            ensure_string,
            default_value(lambda env: platform.node()),
            "Automatically set to the name of the current host.",
        ),
        "HOSTTYPE": Var(
            is_string,
            ensure_string,
            ensure_string,
            default_value(lambda env: platform.machine()),
            "Automatically set to a string that fully describes the system type on which xonsh is executing.",
        ),
        "IGNOREEOF": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Prevents Ctrl-D from exiting the shell.",
        ),
        "INDENT": Var(
            is_string,
            ensure_string,
            ensure_string,
            "    ",
            "Indentation string for multiline input",
        ),
        "INTENSIFY_COLORS_ON_WIN": Var(
            always_false,
            intensify_colors_on_win_setter,
            bool_to_str,
            True,
            "Enhance style colors for readability "
            "when using the default terminal (``cmd.exe``) on Windows. Blue colors, "
            "which are hard to read, are replaced with cyan. Other colors are "
            "generally replaced by their bright counter parts.",
            doc_configurable=ON_WINDOWS,
        ),
        "LANG": Var(
            is_string,
            ensure_string,
            ensure_string,
            "C.UTF-8",
            "Fallback locale setting for systems where it matters",
        ),
        "LC_COLLATE": Var(
            always_false,
            locale_convert("LC_COLLATE"),
            ensure_string,
            locale.setlocale(locale.LC_COLLATE),
        ),
        "LC_CTYPE": Var(
            always_false,
            locale_convert("LC_CTYPE"),
            ensure_string,
            locale.setlocale(locale.LC_CTYPE),
        ),
        "LC_MONETARY": Var(
            always_false,
            locale_convert("LC_MONETARY"),
            ensure_string,
            locale.setlocale(locale.LC_MONETARY),
        ),
        "LC_NUMERIC": Var(
            always_false,
            locale_convert("LC_NUMERIC"),
            ensure_string,
            locale.setlocale(locale.LC_NUMERIC),
        ),
        "LC_TIME": Var(
            always_false,
            locale_convert("LC_TIME"),
            ensure_string,
            locale.setlocale(locale.LC_TIME),
        ),
        "LS_COLORS": Var(
            is_lscolors,
            LsColors.convert,
            detype,
            default_lscolors,
            "Color settings for ``ls`` command line utility and, "
            "with ``$SHELL_TYPE='prompt_toolkit'``, file arguments in subprocess mode.",
            doc_default="``*.7z=1;0;31:*.Z=1;0;31:*.aac=0;36:*.ace=1;0;31:"
            "*.alz=1;0;31:*.arc=1;0;31:*.arj=1;0;31:*.asf=1;0;35:*.au=0;36:"
            "*.avi=1;0;35:*.bmp=1;0;35:*.bz=1;0;31:*.bz2=1;0;31:*.cab=1;0;31:"
            "*.cgm=1;0;35:*.cpio=1;0;31:*.deb=1;0;31:*.dl=1;0;35:*.dwm=1;0;31:"
            "*.dz=1;0;31:*.ear=1;0;31:*.emf=1;0;35:*.esd=1;0;31:*.flac=0;36:"
            "*.flc=1;0;35:*.fli=1;0;35:*.flv=1;0;35:*.gif=1;0;35:*.gl=1;0;35:"
            "*.gz=1;0;31:*.jar=1;0;31:*.jpeg=1;0;35:*.jpg=1;0;35:*.lha=1;0;31:"
            "*.lrz=1;0;31:*.lz=1;0;31:*.lz4=1;0;31:*.lzh=1;0;31:*.lzma=1;0;31"
            ":*.lzo=1;0;31:*.m2v=1;0;35:*.m4a=0;36:*.m4v=1;0;35:*.mid=0;36:"
            "*.midi=0;36:*.mjpeg=1;0;35:*.mjpg=1;0;35:*.mka=0;36:*.mkv=1;0;35:"
            "*.mng=1;0;35:*.mov=1;0;35:*.mp3=0;36:*.mp4=1;0;35:*.mp4v=1;0;35:"
            "*.mpc=0;36:*.mpeg=1;0;35:*.mpg=1;0;35:*.nuv=1;0;35:*.oga=0;36:"
            "*.ogg=0;36:*.ogm=1;0;35:*.ogv=1;0;35:*.ogx=1;0;35:*.opus=0;36:"
            "*.pbm=1;0;35:*.pcx=1;0;35:*.pgm=1;0;35:*.png=1;0;35:*.ppm=1;0;35:"
            "*.qt=1;0;35:*.ra=0;36:*.rar=1;0;31:*.rm=1;0;35:*.rmvb=1;0;35:"
            "*.rpm=1;0;31:*.rz=1;0;31:*.sar=1;0;31:*.spx=0;36:*.svg=1;0;35:"
            "*.svgz=1;0;35:*.swm=1;0;31:*.t7z=1;0;31:*.tar=1;0;31:*.taz=1;0;31:"
            "*.tbz=1;0;31:*.tbz2=1;0;31:*.tga=1;0;35:*.tgz=1;0;31:*.tif=1;0;35:"
            "*.tiff=1;0;35:*.tlz=1;0;31:*.txz=1;0;31:*.tz=1;0;31:*.tzo=1;0;31:"
            "*.tzst=1;0;31:*.vob=1;0;35:*.war=1;0;31:*.wav=0;36:*.webm=1;0;35:"
            "*.wim=1;0;31:*.wmv=1;0;35:*.xbm=1;0;35:*.xcf=1;0;35:*.xpm=1;0;35:"
            "*.xspf=0;36:*.xwd=1;0;35:*.xz=1;0;31:*.yuv=1;0;35:*.z=1;0;31:"
            "*.zip=1;0;31:*.zoo=1;0;31:*.zst=1;0;31:bd=40;0;33:ca=0;30;41:"
            "cd=40;0;33:di=1;0;34:do=1;0;35:ex=1;0;32:ln=1;0;36:mh=0:mi=0:"
            "or=40;0;31:ow=0;34;42:pi=40;0;33:rs=0:sg=0;30;43:so=1;0;35:"
            "st=0;37;44:su=0;37;41:tw=0;30;42``",
        ),
        "LOADED_RC_FILES": Var(
            is_bool_seq,
            csv_to_bool_seq,
            bool_seq_to_csv,
            (),
            "Whether or not any of the xonsh run control files were loaded at "
            "startup. This is a sequence of bools in Python that is converted "
            "to a CSV list in string form, ie ``[True, False]`` becomes "
            "``'True,False'``.",
            doc_configurable=False,
        ),
        "MOUSE_SUPPORT": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Enable mouse support in the ``prompt_toolkit`` shell. This allows "
            "clicking for positioning the cursor or selecting a completion. In "
            "some terminals however, this disables the ability to scroll back "
            "through the history of the terminal. Only usable with "
            "``$SHELL_TYPE=prompt_toolkit``",
        ),
        "MULTILINE_PROMPT": Var(
            is_string_or_callable,
            ensure_string,
            ensure_string,
            ".",
            "Prompt text for 2nd+ lines of input, may be str or function which "
            "returns a str.",
        ),
        "OLDPWD": Var(
            is_string,
            ensure_string,
            ensure_string,
            ".",
            "Used to represent a previous present working directory.",
            doc_configurable=False,
        ),
        "PATH": Var(
            is_env_path,
            str_to_env_path,
            env_path_to_str,
            PATH_DEFAULT,
            "List of strings representing where to look for executables.",
            doc_default="On Windows: it is ``Path`` value of register's "
            "``HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment``. "
            "On Mac OSX: ``('/usr/local/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin')`` "
            "On Linux & on Cygwin & on MSYS, when detected that the distro "
            "is like arch, the default PATH is "
            "``('/usr/local/sbin', '/usr/local/bin', '/usr/bin', "
            "'/usr/bin/site_perl', '/usr/bin/vendor_perl', '/usr/bin/core_perl')``"
            " and otherwise is "
            "``('~/bin', '/usr/local/sbin', '/usr/local/bin', '/usr/sbin',"
            "'/usr/bin', '/sbin', '/bin', '/usr/games', '/usr/local/games')``",
        ),
        re.compile(r"\w*PATH$"): Var(is_env_path, str_to_env_path, env_path_to_str),
        re.compile(r"\w*DIRS$"): Var(is_env_path, str_to_env_path, env_path_to_str),
        "PATHEXT": Var(
            is_nonstring_seq_of_strings,
            pathsep_to_upper_seq,
            seq_to_upper_pathsep,
            [".COM", ".EXE", ".BAT", ".CMD"] if ON_WINDOWS else [],
            "Sequence of extension strings (eg, ``.EXE``) for "
            "filtering valid executables by. Each element must be "
            "uppercase.",
        ),
        "PRETTY_PRINT_RESULTS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            'Flag for "pretty printing" return values.',
        ),
        "PROMPT": Var(
            is_string_or_callable,
            ensure_string,
            ensure_string,
            prompt.default_prompt(),
            "The prompt text. May contain keyword arguments which are "
            "auto-formatted, see 'Customizing the Prompt' at "
            "http://xon.sh/tutorial.html#customizing-the-prompt. "
            "This value is never inherited from parent processes.",
            doc_default="``xonsh.environ.DEFAULT_PROMPT``",
        ),
        "PROMPT_FIELDS": Var(
            always_true,
            None,
            None,
            prompt.PROMPT_FIELDS,
            "Dictionary containing variables to be used when formatting $PROMPT "
            "and $TITLE. See 'Customizing the Prompt' "
            "http://xon.sh/tutorial.html#customizing-the-prompt",
            doc_configurable=False,
            doc_default="``xonsh.prompt.PROMPT_FIELDS``",
        ),
        "PROMPT_REFRESH_INTERVAL": Var(
            is_float,
            float,
            str,
            0,
            "Interval (in seconds) to evaluate and update ``$PROMPT``, ``$RIGHT_PROMPT`` "
            "and ``$BOTTOM_TOOLBAR``. The default is zero (no update). "
            "NOTE: ``$UPDATE_PROMPT_ON_KEYPRESS`` must be set to ``True`` for this "
            "variable to take effect.",
        ),
        "PROMPT_TOOLKIT_COLOR_DEPTH": Var(
            always_false,
            ptk2_color_depth_setter,
            ensure_string,
            "",
            "The color depth used by prompt toolkit 2. Possible values are: "
            "``DEPTH_1_BIT``, ``DEPTH_4_BIT``, ``DEPTH_8_BIT``, ``DEPTH_24_BIT`` "
            "colors. Default is an empty string which means that prompt toolkit decide.",
        ),
        "PTK_STYLE_OVERRIDES": Var(
            is_str_str_dict,
            to_str_str_dict,
            dict_to_str,
            dict(PTK2_STYLE),
            "A dictionary containing custom prompt_toolkit style definitions.",
        ),
        "PUSHD_MINUS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Flag for directory pushing functionality. False is the normal "
            "behavior.",
        ),
        "PUSHD_SILENT": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not to suppress directory stack manipulation output.",
        ),
        "RAISE_SUBPROC_ERROR": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not to raise an error if a subprocess (captured or "
            "uncaptured) returns a non-zero exit status, which indicates failure. "
            "This is most useful in xonsh scripts or modules where failures "
            "should cause an end to execution. This is less useful at a terminal. "
            "The error that is raised is a ``subprocess.CalledProcessError``.",
        ),
        "RIGHT_PROMPT": Var(
            is_string_or_callable,
            ensure_string,
            ensure_string,
            "",
            "Template string for right-aligned text "
            "at the prompt. This may be parametrized in the same way as "
            "the ``$PROMPT`` variable. Currently, this is only available in the "
            "prompt-toolkit shell.",
        ),
        "BOTTOM_TOOLBAR": Var(
            is_string_or_callable,
            ensure_string,
            ensure_string,
            "",
            "Template string for the bottom toolbar. "
            "This may be parametrized in the same way as "
            "the ``$PROMPT`` variable. Currently, this is only available in the "
            "prompt-toolkit shell.",
        ),
        "SHELL_TYPE": Var(
            is_string,
            ensure_string,
            ensure_string,
            "best",
            "Which shell is used. Currently two base shell types are supported:\n\n"
            "    - ``readline`` that is backed by Python's readline module\n"
            "    - ``prompt_toolkit`` that uses external library of the same name\n"
            "    - ``random`` selects a random shell from the above on startup\n"
            "    - ``best`` selects the most feature-rich shell available on the\n"
            "       user's system\n\n"
            "To use the ``prompt_toolkit`` shell you need to have the "
            "`prompt_toolkit <https://github.com/jonathanslenders/python-prompt-toolkit>`_"
            " library installed. To specify which shell should be used, do so in "
            "the run control file.",
            doc_default="``best``",
        ),
        "SUBSEQUENCE_PATH_COMPLETION": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Toggles subsequence matching of paths for tab completion. "
            "If ``True``, then, e.g., ``~/u/ro`` can match ``~/lou/carcolh``.",
        ),
        "SUGGEST_COMMANDS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "When a user types an invalid command, xonsh will try to offer "
            "suggestions of similar valid commands if this is True.",
        ),
        "SUGGEST_MAX_NUM": Var(
            is_int,
            int,
            str,
            5,
            "xonsh will show at most this many suggestions in response to an "
            "invalid command. If negative, there is no limit to how many "
            "suggestions are shown.",
        ),
        "SUGGEST_THRESHOLD": Var(
            is_int,
            int,
            str,
            3,
            "An error threshold. If the Levenshtein distance between the entered "
            "command and a valid command is less than this value, the valid "
            'command will be offered as a suggestion.  Also used for "fuzzy" '
            "tab completion of paths.",
        ),
        "SUPPRESS_BRANCH_TIMEOUT_MESSAGE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not to suppress branch timeout warning messages.",
        ),
        "TERM": Var(
            is_string,
            ensure_string,
            ensure_string,
            DefaultNotGiven,
            "TERM is sometimes set by the terminal emulator. This is used (when "
            "valid) to determine whether the terminal emulator can support "
            "the selected shell, or whether or not to set the title. Users shouldn't "
            "need to set this themselves. Note that this variable should be set as "
            "early as possible in order to ensure it is effective. Here are a few "
            "options:\n\n"
            "* Set this from the program that launches xonsh. On POSIX systems, \n"
            "  this can be performed by using env, e.g. \n"
            "  ``/usr/bin/env TERM=xterm-color xonsh`` or similar.\n"
            "* From the xonsh command line, namely ``xonsh -DTERM=xterm-color``.\n"
            '* In the config file with ``{"env": {"TERM": "xterm-color"}}``.\n'
            "* Lastly, in xonshrc with ``$TERM``\n\n"
            "Ideally, your terminal emulator will set this correctly but that does "
            "not always happen.",
            doc_configurable=False,
        ),
        "THREAD_SUBPROCS": Var(
            is_bool_or_none,
            to_bool_or_none,
            bool_or_none_to_str,
            True if not ON_CYGWIN else False,
            "Whether or not to try to run subrocess mode in a Python thread, "
            "when applicable. There are various trade-offs, which normally "
            "affects only interactive sessions.\n\nWhen True:\n\n"
            "* Xonsh is able capture & store the stdin, stdout, and stderr \n"
            "  of threadable subprocesses.\n"
            "* However, stopping threaded subprocs with ^Z (i.e. ``SIGTSTP``)\n"
            "  is disabled as it causes deadlocked terminals.\n"
            "  ``SIGTSTP`` may still be issued and only the physical pressing\n"
            "  of ``Ctrl+Z`` is ignored.\n"
            "* Threadable commands are run with ``PopenThread`` and threadable \n"
            "  aliases are run with ``ProcProxyThread``.\n\n"
            "When False:\n\n"
            "* Xonsh may not be able to capture stdin, stdout, and stderr streams \n"
            "  unless explicitly asked to do so.\n"
            "* Stopping the thread with ``Ctrl+Z`` yields to job control.\n"
            "* Threadable commands are run with ``Popen`` and threadable \n"
            "  alias are run with ``ProcProxy``.\n\n"
            "The desired effect is often up to the command, user, or use case.\n\n"
            "None values are for internal use only and are used to turn off "
            "threading when loading xonshrc files. This is done because Bash "
            "was automatically placing new xonsh instances in the background "
            "at startup when threadable subprocs were used. Please see "
            "https://github.com/xonsh/xonsh/pull/3705 for more information.\n",
        ),
        "TITLE": Var(
            is_string,
            ensure_string,
            ensure_string,
            DEFAULT_TITLE,
            "The title text for the window in which xonsh is running. Formatted "
            "in the same manner as ``$PROMPT``, see 'Customizing the Prompt' "
            "http://xon.sh/tutorial.html#customizing-the-prompt.",
            doc_default="``xonsh.environ.DEFAULT_TITLE``",
        ),
        "UPDATE_COMPLETIONS_ON_KEYPRESS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Completions display is evaluated and presented whenever a key is "
            "pressed. This avoids the need to press TAB, except to cycle through "
            "the possibilities. This currently only affects the prompt-toolkit shell.",
        ),
        "UPDATE_OS_ENVIRON": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "If True ``os_environ`` will always be updated "
            "when the xonsh environment changes. The environment can be reset to "
            "the default value by calling ``__xonsh__.env.undo_replace_env()``",
        ),
        "UPDATE_PROMPT_ON_KEYPRESS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Disables caching the prompt between commands, "
            "so that it would be reevaluated on each keypress. "
            "Disabled by default because of the incurred performance penalty.",
        ),
        "VC_BRANCH_TIMEOUT": Var(
            is_float,
            float,
            str,
            0.2 if ON_WINDOWS else 0.1,
            "The timeout (in seconds) for version control "
            "branch computations. This is a timeout per subprocess call, so the "
            "total time to compute will be larger than this in many cases.",
        ),
        "VC_HG_SHOW_BRANCH": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Whether or not to show the Mercurial branch in the prompt.",
        ),
        "VI_MODE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Flag to enable ``vi_mode`` in the ``prompt_toolkit`` shell.",
        ),
        "VIRTUAL_ENV": Var(
            is_string,
            ensure_string,
            ensure_string,
            DefaultNotGiven,
            "Path to the currently active Python environment.",
            doc_configurable=False,
        ),
        "XDG_CONFIG_HOME": Var(
            is_string,
            ensure_string,
            ensure_string,
            os.path.expanduser(os.path.join("~", ".config")),
            "Open desktop standard configuration home dir. This is the same "
            "default as used in the standard.",
            doc_configurable=False,
            doc_default="``~/.config``",
        ),
        "XDG_DATA_HOME": Var(
            is_string,
            ensure_string,
            ensure_string,
            os.path.expanduser(os.path.join("~", ".local", "share")),
            "Open desktop standard data home dir. This is the same default as "
            "used in the standard.",
            doc_default="``~/.local/share``",
        ),
        "XONSHRC": Var(
            is_env_path,
            str_to_env_path,
            env_path_to_str,
            default_xonshrc,
            "A list of the locations of run control files, if they exist.  User "
            "defined run control file will supersede values set in system-wide "
            "control file if there is a naming collision. $THREAD_SUBPROCS=None "
            "when reading in run control files.",
            doc_default=(
                "On Linux & Mac OSX: ``['/etc/xonshrc', '~/.config/xonsh/rc.xsh', '~/.xonshrc']``\n"
                "\nOn Windows: "
                "``['%ALLUSERSPROFILE%\\\\xonsh\\\\xonshrc', '~/.config/xonsh/rc.xsh', '~/.xonshrc']``"
            ),
        ),
        "XONSH_APPEND_NEWLINE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            xonsh_append_newline,
            "Append new line when a partial line is preserved in output.",
            doc_default="``$XONSH_INTERACTIVE``",
        ),
        "XONSH_AUTOPAIR": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether Xonsh will auto-insert matching parentheses, brackets, and "
            "quotes. Only available under the prompt-toolkit shell.",
        ),
        "XONSH_CACHE_SCRIPTS": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "Controls whether the code for scripts run from xonsh will be cached"
            " (``True``) or re-compiled each time (``False``).",
        ),
        "XONSH_CACHE_EVERYTHING": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Controls whether all code (including code entered at the interactive"
            " prompt) will be cached.",
        ),
        "XONSH_COLOR_STYLE": Var(
            is_string,
            ensure_string,
            ensure_string,
            "default",
            "Sets the color style for xonsh colors. This is a style name, not "
            "a color map. Run ``xonfig styles`` to see the available styles.",
        ),
        "XONSH_CONFIG_DIR": Var(
            is_string,
            ensure_string,
            ensure_string,
            xonsh_config_dir,
            "This is the location where xonsh configuration information is stored.",
            doc_configurable=False,
            doc_default="``$XDG_CONFIG_HOME/xonsh``",
        ),
        "XONSH_DATETIME_FORMAT": Var(
            is_string,
            ensure_string,
            ensure_string,
            "%Y-%m-%d %H:%M",
            "The format that is used for ``datetime.strptime()`` in various places, "
            "i.e the history timestamp option.",
        ),
        "XONSH_DEBUG": Var(
            always_false,
            to_debug,
            bool_or_int_to_str,
            0,
            "Sets the xonsh debugging level. This may be an integer or a boolean. "
            "Setting this variable prior to stating xonsh to ``1`` or ``True`` "
            "will suppress amalgamated imports. Setting it to ``2`` will get some "
            "basic information like input transformation, command replacement. "
            "With ``3`` or a higher number will make more debugging information "
            "presented, like PLY parsing messages.",
            doc_configurable=False,
        ),
        "XONSH_DATA_DIR": Var(
            is_string,
            ensure_string,
            ensure_string,
            xonsh_data_dir,
            "This is the location where xonsh data files are stored, such as "
            "history.",
            doc_default="``$XDG_DATA_HOME/xonsh``",
        ),
        "XONSH_ENCODING": Var(
            is_string,
            ensure_string,
            ensure_string,
            DEFAULT_ENCODING,
            "This is the encoding that xonsh should use for subprocess operations.",
            doc_default="``sys.getdefaultencoding()``",
        ),
        "XONSH_ENCODING_ERRORS": Var(
            is_string,
            ensure_string,
            ensure_string,
            "surrogateescape",
            "The flag for how to handle encoding errors should they happen. "
            "Any string flag that has been previously registered with Python "
            "is allowed. See the 'Python codecs documentation' "
            "(https://docs.python.org/3/library/codecs.html#error-handlers) "
            "for more information and available options.",
            doc_default="``surrogateescape``",
        ),
        "XONSH_GITSTATUS_*": Var(
            is_string,
            ensure_string,
            ensure_string,
            "",
            "Symbols for gitstatus prompt. Default values are: \n\n"
            "* ``XONSH_GITSTATUS_HASH``: ``:``\n"
            "* ``XONSH_GITSTATUS_BRANCH``: ``{CYAN}``\n"
            "* ``XONSH_GITSTATUS_OPERATION``: ``{CYAN}``\n"
            "* ``XONSH_GITSTATUS_STAGED``: ``{RED}●``\n"
            "* ``XONSH_GITSTATUS_CONFLICTS``: ``{RED}×``\n"
            "* ``XONSH_GITSTATUS_CHANGED``: ``{BLUE}+``\n"
            "* ``XONSH_GITSTATUS_UNTRACKED``: ``…``\n"
            "* ``XONSH_GITSTATUS_STASHED``: ``⚑``\n"
            "* ``XONSH_GITSTATUS_CLEAN``: ``{BOLD_GREEN}✓``\n"
            "* ``XONSH_GITSTATUS_AHEAD``: ``↑·``\n"
            "* ``XONSH_GITSTATUS_BEHIND``: ``↓·``\n",
        ),
        "XONSH_HISTORY_BACKEND": Var(
            is_history_backend,
            to_itself,
            ensure_string,
            "json",
            "Set which history backend to use. Options are: 'json', "
            "'sqlite', and 'dummy'. The default is 'json'. "
            "``XONSH_HISTORY_BACKEND`` also accepts a class type that inherits "
            "from ``xonsh.history.base.History``, or its instance.",
        ),
        "XONSH_HISTORY_FILE": Var(
            is_string,
            ensure_string,
            ensure_string,
            os.path.expanduser("~/.xonsh_history.json"),
            "Location of history file (deprecated).",
            doc_configurable=False,
            doc_default="``~/.xonsh_history``",
        ),
        "XONSH_HISTORY_MATCH_ANYWHERE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "When searching history from a partial string (by pressing up arrow), "
            "match command history anywhere in a given line (not just the start)",
            doc_default="False",
        ),
        "XONSH_HISTORY_SIZE": Var(
            is_history_tuple,
            to_history_tuple,
            history_tuple_to_str,
            (8128, "commands"),
            "Value and units tuple that sets the size of history after garbage "
            "collection. Canonical units are:\n\n"
            "- ``commands`` for the number of past commands executed,\n"
            "- ``files`` for the number of history files to keep,\n"
            "- ``s`` for the number of seconds in the past that are allowed, and\n"
            "- ``b`` for the number of bytes that history may consume.\n\n"
            "Common abbreviations, such as '6 months' or '1 GB' are also allowed.",
            doc_default="``(8128, 'commands')`` or ``'8128 commands'``",
        ),
        "XONSH_INTERACTIVE": Var(
            is_bool,
            to_bool,
            bool_to_str,
            True,
            "``True`` if xonsh is running interactively, and ``False`` otherwise.",
            doc_configurable=False,
        ),
        "XONSH_LOGIN": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "``True`` if xonsh is running as a login shell, and ``False`` otherwise.",
            doc_configurable=False,
        ),
        "XONSH_PROC_FREQUENCY": Var(
            is_float,
            float,
            str,
            1e-4,
            "The process frequency is the time that "
            "xonsh process threads sleep for while running command pipelines. "
            "The value has units of seconds [s].",
        ),
        "XONSH_SHOW_TRACEBACK": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Controls if a traceback is shown if exceptions occur in the shell. "
            "Set to ``True`` to always show traceback or ``False`` to always hide. "
            "If undefined then the traceback is hidden but a notice is shown on how "
            "to enable the full traceback.",
        ),
        "XONSH_SOURCE": Var(
            is_string,
            ensure_string,
            ensure_string,
            "",
            "When running a xonsh script, this variable contains the absolute path "
            "to the currently executing script's file.",
            doc_configurable=False,
        ),
        "XONSH_STDERR_PREFIX": Var(
            is_string,
            ensure_string,
            ensure_string,
            "",
            "A format string, using the same keys and colors as ``$PROMPT``, that "
            "is prepended whenever stderr is displayed. This may be used in "
            "conjunction with ``$XONSH_STDERR_POSTFIX`` to close out the block."
            "For example, to have stderr appear on a red background, the "
            'prefix & postfix pair would be "{BACKGROUND_RED}" & "{RESET}".',
        ),
        "XONSH_STDERR_POSTFIX": Var(
            is_string,
            ensure_string,
            ensure_string,
            "",
            "A format string, using the same keys and colors as ``$PROMPT``, that "
            "is appended whenever stderr is displayed. This may be used in "
            "conjunction with ``$XONSH_STDERR_PREFIX`` to start the block."
            "For example, to have stderr appear on a red background, the "
            'prefix & postfix pair would be "{BACKGROUND_RED}" & "{RESET}".',
        ),
        "XONSH_STORE_STDIN": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not to store the stdin that is supplied to the "
            "``!()`` and ``![]`` operators.",
        ),
        "XONSH_STORE_STDOUT": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Whether or not to store the ``stdout`` and ``stderr`` streams in the "
            "history files.",
        ),
        "XONSH_TRACE_SUBPROC": Var(
            is_bool,
            to_bool,
            bool_to_str,
            False,
            "Set to ``True`` to show arguments list of every executed subprocess command.",
        ),
        "XONSH_TRACEBACK_LOGFILE": Var(
            is_logfile_opt,
            to_logfile_opt,
            logfile_opt_to_str,
            None,
            "Specifies a file to store the traceback log to, regardless of whether "
            "``XONSH_SHOW_TRACEBACK`` has been set. Its value must be a writable file "
            "or None / the empty string if traceback logging is not desired. "
            "Logging to a file is not enabled by default.",
        ),
    }

    if hasattr(locale, "LC_MESSAGES"):
        dv["LC_MESSAGES"] = Var(
            always_false,
            locale_convert("LC_MESSAGES"),
            ensure_string,
            locale.setlocale(locale.LC_MESSAGES),
        )

    return dv