def get_otool_out(tools_dir, cmd_type, bin_path, bin_dir):
    """Get otool args by OS and type."""
    if (len(settings.OTOOL_BINARY) > 0
            and is_file_exists(settings.OTOOL_BINARY)):
        otool_bin = settings.OTOOL_BINARY
    else:
        otool_bin = 'otool'
    if (len(settings.JTOOL_BINARY) > 0
            and is_file_exists(settings.JTOOL_BINARY)):
        jtool_bin = settings.JTOOL_BINARY
    else:
        jtool_bin = os.path.join(tools_dir, 'jtool.ELF64')
    jtool2_bin = os.path.join(tools_dir, 'jtool2.ELF64')
    # jtool execute permission check
    for toolbin in [jtool_bin, jtool2_bin]:
        if not os.access(toolbin, os.X_OK):
            os.chmod(toolbin, stat.S_IEXEC)
    plat = platform.system()
    if cmd_type == 'libs':
        if plat == 'Darwin':
            args = [otool_bin, '-L', bin_path]
            args2 = args
        elif plat == 'Linux':
            args = [jtool_bin, '-arch', 'arm', '-L', '-v', bin_path]
            args2 = [jtool2_bin, '-L', '-v', '-q', bin_path]
        else:
            # Platform Not Supported
            return None
        try:
            libs = subprocess.check_output(args2).decode('utf-8', 'ignore')
        except Exception:
            libs = subprocess.check_output(args).decode('utf-8', 'ignore')
        libs = smart_text(escape(libs.replace(bin_dir + '/', '')))
        return libs.split('\n')
    elif cmd_type == 'header':
        if plat == 'Darwin':
            args = [otool_bin, '-hv', bin_path]
            args2 = args
        elif plat == 'Linux':
            args = [jtool_bin, '-arch', 'arm', '-h', '-v', bin_path]
            args2 = [jtool2_bin, '-h', '-v', '-q', bin_path]
        else:
            # Platform Not Supported
            return None
        try:
            return subprocess.check_output(args2)
        except Exception:
            return subprocess.check_output(args)
    elif cmd_type == 'symbols':
        if plat == 'Darwin':
            args = [otool_bin, '-Iv', bin_path]
            return subprocess.check_output(args)
        elif plat == 'Linux':
            args = [jtool_bin, '-arch', 'arm', '-S', bin_path]
            arg2 = [jtool2_bin, '-S', bin_path]
            try:
                with open(os.devnull, 'w') as devnull:
                    return subprocess.check_output(arg2, stderr=devnull)
            except Exception:
                return subprocess.check_output(args)
        else:
            # Platform Not Supported
            return None
    elif cmd_type == 'classdump':
        # Handle Classdump in Linux
        # Add timeout to handle ULEB128 malformed
        return [jtool_bin, '-arch', 'arm', '-d', 'objc', '-v', bin_path]
    return None