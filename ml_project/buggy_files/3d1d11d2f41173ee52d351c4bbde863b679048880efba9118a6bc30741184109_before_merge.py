def adb_command(cmd_list, shell=False, silent=False):
        emulator = get_identifier()
        adb = getADB()

        args = [adb,
                "-s",
                emulator]
        if shell:
            args += ['shell']
        args += cmd_list

        try:
            result = subprocess.check_output(args)
            return result
        except:
            if not silent:
                PrintException("[ERROR] adb_command")
            return None