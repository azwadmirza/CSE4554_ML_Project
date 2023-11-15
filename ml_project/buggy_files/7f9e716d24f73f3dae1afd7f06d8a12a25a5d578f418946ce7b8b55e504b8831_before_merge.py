    def add(self, cmd, allow_duplicates=False):
        """
        Add a new command or commands to this CmdSet, a list of
        commands or a cmdset to this cmdset. Note that this is *not*
        a merge operation (that is handled by the + operator).

        Args:
            cmd (Command, list, Cmdset): This allows for adding one or
                more commands to this Cmdset in one go. If another Cmdset
                is given, all its commands will be added.
            allow_duplicates (bool, optional): If set, will not try to remove
                duplicate cmds in the set. This is needed during the merge process
                to avoid wiping commands coming from cmdsets with duplicate=True.

        Notes:
            If cmd already exists in set, it will replace the old one
            (no priority checking etc happens here). This is very useful
            when overloading default commands).

            If cmd is another cmdset class or -instance, the commands of
            that command set is added to this one, as if they were part of
            the original cmdset definition. No merging or priority checks
            are made, rather later added commands will simply replace
            existing ones to make a unique set.

        """

        if inherits_from(cmd, "evennia.commands.cmdset.CmdSet"):
            # cmd is a command set so merge all commands in that set
            # to this one. We raise a visible error if we created
            # an infinite loop (adding cmdset to itself somehow)
            try:
                cmd = self._instantiate(cmd)
            except RuntimeError:
                string = "Adding cmdset %(cmd)s to %(class)s lead to an "
                string += "infinite loop. When adding a cmdset to another, "
                string += "make sure they are not themself cyclically added to "
                string += "the new cmdset somewhere in the chain."
                raise RuntimeError(_(string) % {"cmd": cmd, "class": self.__class__})
            cmds = cmd.commands
        elif is_iter(cmd):
            cmds = [self._instantiate(c) for c in cmd]
        else:
            cmds = [self._instantiate(cmd)]
        commands = self.commands
        system_commands = self.system_commands
        for cmd in cmds:
            # add all commands
            if not hasattr(cmd, "obj"):
                cmd.obj = self.cmdsetobj
            try:
                ic = commands.index(cmd)
                commands[ic] = cmd  # replace
            except ValueError:
                commands.append(cmd)
            self.commands = commands
            if not allow_duplicates:
                # extra run to make sure to avoid doublets
                self.commands = list(set(self.commands))
            # add system_command to separate list as well,
            # for quick look-up
            if cmd.key.startswith("__"):
                try:
                    ic = system_commands.index(cmd)
                    system_commands[ic] = cmd  # replace
                except ValueError:
                    system_commands.append(cmd)