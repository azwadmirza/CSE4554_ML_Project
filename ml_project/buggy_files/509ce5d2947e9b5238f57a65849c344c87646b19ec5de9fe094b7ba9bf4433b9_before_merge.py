def convert_config_to_tribler74(state_dir=None):
    """
    Convert the download config files to Tribler 7.4 format. The extensions will also be renamed from .state to .conf
    """
    if PY3:
        from lib2to3.refactor import RefactoringTool, get_fixers_from_package
        refactoring_tool = RefactoringTool(fixer_names=get_fixers_from_package('lib2to3.fixes'))

    state_dir = state_dir or TriblerConfig.get_default_state_dir()
    for _, filename in enumerate(iglob(os.path.join(state_dir, STATEDIR_CHECKPOINT_DIR, '*.state'))):
        old_config = CallbackConfigParser()
        try:
            old_config.read_file(filename)
        except MissingSectionHeaderError:
            logger.error("Removing download state file %s since it appears to be corrupt", filename)
            os.remove(filename)

        # We first need to fix the .state file such that it has the correct metainfo/resumedata
        for section, option in [('state', 'metainfo'), ('state', 'engineresumedata')]:
            value = old_config.get(section, option, literal_eval=False)
            if PY3:
                value = re.sub(r":[^b]('|\").*?[^\\]\1", lambda x: ': b' + x.group(0)[2:], value)
                value = re.sub(r"[{| ]('|\").*?[^\\]\1:", lambda x: x.group()[:1] + 'b' + x.group()[1:], value)
                value = str(refactoring_tool.refactor_string(value+'\n', option + '_2to3'))
            try:
                value = ast.literal_eval(value)
                old_config.set(section, option, base64.b64encode(lt.bencode(value)).decode('utf-8'))
            except (ValueError, SyntaxError):
                logger.error("Removing download state file %s since it could not be converted", filename)
                os.remove(filename)
                continue

        # Remove dlstate since the same information is already stored in the resumedata
        if old_config.has_option('state', 'dlstate'):
            old_config.remove_option('state', 'dlstate')

        new_config = ConfigObj(infile=filename[:-6] + '.conf', encoding='utf8')
        for section in old_config.sections():
            for key, _ in old_config.items(section):
                val = old_config.get(section, key)
                if section not in new_config:
                    new_config[section] = {}
                new_config[section][key] = val
        new_config.write()
        os.remove(filename)