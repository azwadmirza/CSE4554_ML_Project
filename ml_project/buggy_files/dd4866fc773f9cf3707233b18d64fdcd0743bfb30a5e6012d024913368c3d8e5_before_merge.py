    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        ''' handler for file transfer operations '''

        if self.runner.noop_on_check(inject):
            # in check mode, always skip this module
            return ReturnData(conn=conn, comm_ok=True, result=dict(skipped=True, msg='check mode not supported for this module'))

        tokens  = shlex.split(module_args)
        source  = tokens[0]
        # FIXME: error handling
        args    = " ".join(tokens[1:])
        source  = template.template(self.runner.basedir, source, inject)
        if '_original_file' in inject:
            source = utils.path_dwim_relative(inject['_original_file'], 'files', source, self.runner.basedir)
        else:
            source = utils.path_dwim(self.runner.basedir, source)

        # transfer the file to a remote tmp location
        source  = source.replace('\x00','') # why does this happen here?
        args    = args.replace('\x00','') # why does this happen here?
        tmp_src = os.path.join(tmp, os.path.basename(source))
        tmp_src = tmp_src.replace('\x00', '') 

        conn.put_file(source, tmp_src)

        # fix file permissions when the copy is done as a different user
        if self.runner.sudo and self.runner.sudo_user != 'root':
            prepcmd = 'chmod a+rx %s' % tmp_src
        else:
            prepcmd = 'chmod +x %s' % tmp_src

        # add preparation steps to one ssh roundtrip executing the script
        env_string = self.runner._compute_environment_string(inject)
        module_args = prepcmd + '; ' + env_string + tmp_src + ' ' + args

        handler = utils.plugins.action_loader.get('raw', self.runner)
        result = handler.run(conn, tmp, 'raw', module_args, inject)

        # clean up after
        if tmp.find("tmp") != -1 and not C.DEFAULT_KEEP_REMOTE_FILES:
            self.runner._low_level_exec_command(conn, 'rm -rf %s >/dev/null 2>&1' % tmp, tmp)

        return result