    def _copy_zip_file(self, dest, files, directories, task_vars, tmp):
        # create local zip file containing all the files and directories that
        # need to be copied to the server
        if self._play_context.check_mode:
            module_return = dict(changed=True)
            return module_return

        try:
            zip_file = self._create_zip_tempfile(files, directories)
        except Exception as e:
            module_return = dict(
                changed=False,
                failed=True,
                msg="failed to create tmp zip file: %s" % to_text(e),
                exception=traceback.format_exc()
            )
            return module_return

        zip_path = self._loader.get_real_file(zip_file)

        # send zip file to remote, file must end in .zip so
        # Com Shell.Application works
        tmp_src = self._connection._shell.join_path(tmp, 'source.zip')
        self._transfer_file(zip_path, tmp_src)

        # run the explode operation of win_copy on remote
        copy_args = self._task.args.copy()
        copy_args.update(
            dict(
                src=tmp_src,
                dest=dest,
                mode="explode"
            )
        )
        copy_args.pop('content', None)
        module_return = self._execute_module(module_name='copy',
                                             module_args=copy_args,
                                             task_vars=task_vars)
        shutil.rmtree(os.path.dirname(zip_path))
        return module_return