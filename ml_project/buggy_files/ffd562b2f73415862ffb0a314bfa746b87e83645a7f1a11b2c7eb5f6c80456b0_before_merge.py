    def _fix_state_config(config):
        for section, option in [('state', 'metainfo'), ('state', 'engineresumedata')]:
            value = config.get(section, option, literal_eval=False)
            try:
                value = str(refactoring_tool.refactor_string(value + '\n', option + '_2to3'))
                ungarbled_dict = recursive_ungarble_metainfo(ast.literal_eval(value))
                value = ungarbled_dict or ast.literal_eval(value)
                config.set(section, option, base64.b64encode(lt.bencode(value)).decode('utf-8'))
            except (ValueError, SyntaxError, ParseError) as ex:
                logger.error("Config could not be fixed, probably corrupted. Exception: %s %s", type(ex), str(ex))
                return None
        return config