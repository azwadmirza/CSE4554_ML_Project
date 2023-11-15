def help(command, shell):
    # sys.argv[1] will be ..checkenv in activate if an environment is already
    # activated
    # get grandparent process name to see which shell we're using
    if command in ('..activate', '..checkenv'):
        if shell in ["cmd.exe", "powershell.exe"]:
            raise CondaSystemExit("""Usage: activate ENV

Adds the 'Scripts' and 'Library\\bin' directory of the environment ENV to the front of PATH.
ENV may either refer to just the name of the environment, or the full
prefix path.""")

        else:
            raise CondaSystemExit("""Usage: source activate ENV

Adds the 'bin' directory of the environment ENV to the front of PATH.
ENV may either refer to just the name of the environment, or the full
prefix path.""")
    elif command == '..deactivate':
        if shell in ["cmd.exe", "powershell.exe"]:
            raise CondaSystemExit("""Usage: deactivate

Removes the environment prefix, 'Scripts' and 'Library\\bin' directory
of the environment ENV from the front of PATH.""")
        else:
            raise CondaSystemExit("""Usage: source deactivate

Removes the 'bin' directory of the environment activated with 'source
activate' from PATH. """)
    else:
        raise CondaSystemExit("No help available for command %s" % ensure_text_type(sys.argv[1]))