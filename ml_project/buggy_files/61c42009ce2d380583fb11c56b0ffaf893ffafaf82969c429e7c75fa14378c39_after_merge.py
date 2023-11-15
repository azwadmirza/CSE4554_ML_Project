def convert_config_to_tribler74(state_dir=None):
    """
    Convert the download config files to Tribler 7.4 format. The extensions will also be renamed from .state to .conf
    """
    refactoring_tool = None
    if PY3:
        from lib2to3.refactor import RefactoringTool, get_fixers_from_package
        refactoring_tool = RefactoringTool(fixer_names=get_fixers_from_package('lib2to3.fixes'))

    state_dir = state_dir or TriblerConfig.get_default_base_state_dir()
    for _, filename in enumerate(iglob(os.path.join(state_dir, STATEDIR_CHECKPOINT_DIR, '*.state'))):
        convert_state_file_to_conf_74(filename, refactoring_tool=refactoring_tool)