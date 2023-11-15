def replace_long_shebang(mode, data):
    if mode is FileMode.text:
        shebang_match = SHEBANG_REGEX.match(data)
        if shebang_match:
            whole_shebang, executable, options = shebang_match.groups()
            if len(whole_shebang) > 127:
                executable_name = executable.decode(UTF8).split('/')[-1]
                new_shebang = '#!/usr/bin/env %s%s' % (executable_name, options.decode(UTF8))
                data = data.replace(whole_shebang, new_shebang.encode(UTF8))
    else:
        # TODO: binary shebangs exist; figure this out in the future if text works well
        log.debug("TODO: binary shebangs exist; figure this out in the future if text works well")
    return data