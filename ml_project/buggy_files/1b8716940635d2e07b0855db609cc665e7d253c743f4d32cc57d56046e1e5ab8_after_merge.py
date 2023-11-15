    def run(self):

        '''
        Run the given playbook, based on the settings in the play which
        may limit the runs to serialized groups, etc.
        '''

        signal.signal(signal.SIGINT, self._cleanup)

        result = 0
        entrylist = []
        entry = {}
        try:
            for playbook_path in self._playbooks:
                pb = Playbook.load(playbook_path, variable_manager=self._variable_manager, loader=self._loader)
                self._inventory.set_playbook_basedir(os.path.dirname(playbook_path))

                if self._tqm is None: # we are doing a listing
                    entry = {'playbook': playbook_path}
                    entry['plays'] = []
                else:
                    # make sure the tqm has callbacks loaded
                    self._tqm.load_callbacks()
                    self._tqm.send_callback('v2_playbook_on_start', pb)

                i = 1
                plays = pb.get_plays()
                display.vv('%d plays in %s' % (len(plays), playbook_path))

                for play in plays:
                    if play._included_path is not None:
                        self._loader.set_basedir(play._included_path)
                    else:
                        self._loader.set_basedir(pb._basedir)

                    # clear any filters which may have been applied to the inventory
                    self._inventory.remove_restriction()

                    if play.vars_prompt:
                        for var in play.vars_prompt:
                            vname     = var['name']
                            prompt    = var.get("prompt", vname)
                            default   = var.get("default", None)
                            private   = var.get("private", True)
                            confirm   = var.get("confirm", False)
                            encrypt   = var.get("encrypt", None)
                            salt_size = var.get("salt_size", None)
                            salt      = var.get("salt", None)

                            if vname not in self._variable_manager.extra_vars:
                                if self._tqm:
                                    self._tqm.send_callback('v2_playbook_on_vars_prompt', vname, private, prompt, encrypt, confirm, salt_size, salt, default)
                                    play.vars[vname] = display.do_var_prompt(vname, private, prompt, encrypt, confirm, salt_size, salt, default)
                                else: # we are either in --list-<option> or syntax check
                                    play.vars[vname] = default

                    # Create a temporary copy of the play here, so we can run post_validate
                    # on it without the templating changes affecting the original object.
                    all_vars = self._variable_manager.get_vars(loader=self._loader, play=play)
                    templar = Templar(loader=self._loader, variables=all_vars)
                    new_play = play.copy()
                    new_play.post_validate(templar)

                    if self._options.syntax:
                        continue

                    if self._tqm is None:
                        # we are just doing a listing
                        entry['plays'].append(new_play)

                    else:
                        self._tqm._unreachable_hosts.update(self._unreachable_hosts)

                        # we are actually running plays
                        for batch in self._get_serialized_batches(new_play):
                            if len(batch) == 0:
                                self._tqm.send_callback('v2_playbook_on_play_start', new_play)
                                self._tqm.send_callback('v2_playbook_on_no_hosts_matched')
                                break

                            # restrict the inventory to the hosts in the serialized batch
                            self._inventory.restrict_to_hosts(batch)
                            # and run it...
                            result = self._tqm.run(play=play)

                            # check the number of failures here, to see if they're above the maximum
                            # failure percentage allowed, or if any errors are fatal. If either of those
                            # conditions are met, we break out, otherwise we only break out if the entire
                            # batch failed
                            failed_hosts_count = len(self._tqm._failed_hosts) + len(self._tqm._unreachable_hosts)
                            if new_play.max_fail_percentage is not None and \
                               int((new_play.max_fail_percentage)/100.0 * len(batch)) > int((len(batch) - failed_hosts_count) / len(batch) * 100.0):
                                break
                            elif len(batch) == failed_hosts_count:
                                break

                            # clear the failed hosts dictionaires in the TQM for the next batch
                            self._unreachable_hosts.update(self._tqm._unreachable_hosts)
                            self._tqm.clear_failed_hosts()

                        # if the last result wasn't zero or 3 (some hosts were unreachable),
                        # break out of the serial batch loop
                        if result not in (0, 3):
                            break

                    i = i + 1 # per play

                if entry:
                    entrylist.append(entry) # per playbook

                # send the stats callback for this playbook
                if self._tqm is not None:
                    if C.RETRY_FILES_ENABLED:
                        retries = list(set(self._tqm._failed_hosts.keys() + self._tqm._unreachable_hosts.keys()))
                        retries.sort()
                        if len(retries) > 0:
                            if C.RETRY_FILES_SAVE_PATH:
                                basedir = C.shell_expand(C.RETRY_FILES_SAVE_PATH)
                            else:
                                basedir = os.path.dirname(playbook_path)

                            (retry_name, _) = os.path.splitext(os.path.basename(playbook_path))
                            filename = os.path.join(basedir, "%s.retry" % retry_name)
                            if self._generate_retry_inventory(filename, retries):
                                display.display("\tto retry, use: --limit @%s\n" % filename)

                    self._tqm.send_callback('v2_playbook_on_stats', self._tqm._stats)

                # if the last result wasn't zero, break out of the playbook file name loop
                if result != 0:
                    break

            if entrylist:
                return entrylist

        finally:
            if self._tqm is not None:
                self._cleanup()

        if self._options.syntax:
            display.display("No issues encountered")
            return result

        return result