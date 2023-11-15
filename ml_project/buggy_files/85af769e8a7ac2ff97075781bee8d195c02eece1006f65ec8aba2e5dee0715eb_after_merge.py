def get_file_parser(hostsfile, groups, loader):
    # check to see if the specified file starts with a
    # shebang (#!/), so if an error is raised by the parser
    # class we can show a more apropos error

    shebang_present = False
    processed = False
    myerr = []
    parser = None

    try:
        with open(hostsfile, 'rb') as inv_file:
            initial_chars = inv_file.read(2)
            if initial_chars.startswith(b'#!'):
                shebang_present = True
    except:
        pass

    #FIXME: make this 'plugin loop'
    # script
    if loader.is_executable(hostsfile):
        try:
            parser = InventoryScript(loader=loader, groups=groups, filename=hostsfile)
            processed = True
        except Exception as e:
            myerr.append('Attempted to execute "%s" as inventory script: %s' % (hostsfile, to_native(e)))
    elif shebang_present:

        myerr.append("The inventory file \'%s\' looks like it should be an executable inventory script, but is not marked executable. Perhaps you want to correct this with `chmod +x %s`?" % (hostsfile, hostsfile))

    # YAML/JSON
    if not processed and not shebang_present and os.path.splitext(hostsfile)[-1] in C.YAML_FILENAME_EXTENSIONS:
        try:
            parser = InventoryYAMLParser(loader=loader, groups=groups, filename=hostsfile)
            processed = True
        except Exception as e:
            myerr.append('Attempted to read "%s" as YAML: %s' % (to_native(hostsfile), to_native(e)))

    # ini
    if not processed and not shebang_present:
        try:
            parser = InventoryINIParser(loader=loader, groups=groups, filename=hostsfile)
            processed = True
        except Exception as e:
            myerr.append('Attempted to read "%s" as ini file: %s ' % (to_native(hostsfile), to_native(e)))

    if not processed and myerr:
        raise AnsibleError('\n'.join(myerr))

    return parser