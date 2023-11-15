def convert_state_file_to_conf_74(filename, refactoring_tool=None):
    """
    Converts .pstate file (pre-7.4.0) to .conf file.
    :param filename: .pstate file
    :param refactoring_tool: RefactoringTool instance if using Python3
    :return: fixed config
    """
    def _fix_state_config(config):
        for section, option in [('state', 'metainfo'), ('state', 'engineresumedata')]:
            value = config.get(section, option, literal_eval=False)
            if not value or not refactoring_tool:
                continue

            try:
                value = str(refactoring_tool.refactor_string(value + '\n', option + '_2to3'))
                ungarbled_dict = recursive_ungarble_metainfo(ast.literal_eval(value))
                value = ungarbled_dict or ast.literal_eval(value)
                config.set(section, option, base64.b64encode(lt.bencode(value)).decode('utf-8'))
            except (ValueError, SyntaxError, ParseError) as ex:
                logger.error("Config could not be fixed, probably corrupted. Exception: %s %s", type(ex), str(ex))
                return None
        return config

    old_config = CallbackConfigParser()
    try:
        old_config.read_file(str(filename))
    except MissingSectionHeaderError:
        logger.error("Removing download state file %s since it appears to be corrupt", filename)
        os.remove(filename)

    # We first need to fix the .state file such that it has the correct metainfo/resumedata.
    # If the config cannot be fixed, it is likely corrupted in which case we simply remove the file.
    fixed_config = _fix_state_config(old_config)
    if not fixed_config:
        logger.error("Removing download state file %s since it could not be fixed", filename)
        os.remove(filename)
        return

    # Remove dlstate since the same information is already stored in the resumedata
    if old_config.has_option('state', 'dlstate'):
        old_config.remove_option('state', 'dlstate')

        try:
            conf_filename = str(filename)[:-6] + '.conf'
            new_config = load_config(conf_filename)
            for section in old_config.sections():
                for key, _ in old_config.items(section):
                    val = old_config.get(section, key)
                    if section not in new_config:
                        new_config[section] = {}
                    new_config[section][key] = val
            new_config.write()
            os.remove(filename)
        except ConfigObjParseError:
            logger.error("Could not parse %s file on upgrade so removing it", filename)
            os.remove(filename)

    return fixed_config