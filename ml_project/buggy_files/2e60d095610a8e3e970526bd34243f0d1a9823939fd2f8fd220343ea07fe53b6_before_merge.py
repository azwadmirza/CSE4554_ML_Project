    def get_source(self, environment, template):
        '''
        Salt-specific loader to find imported jinja files.

        Jinja imports will be interpreted as originating from the top
        of each of the directories in the searchpath when the template
        name does not begin with './' or '../'.  When a template name
        begins with './' or '../' then the import will be relative to
        the importing file.

        '''
        # FIXME: somewhere do seprataor replacement: '\\' => '/'
        _template = template
        if template.split('/', 1)[0] in ('..', '.'):
            is_relative = True
        else:
            is_relative = False
        # checks for relative '..' paths that step-out of file_roots
        if is_relative:
            # Starts with a relative path indicator

            if not environment or 'tpldir' not in environment.globals:
                log.warning(
                    'Relative path "%s" cannot be resolved without an environment',
                    template
                )
                raise TemplateNotFound
            base_path = environment.globals['tpldir']
            _template = os.path.normpath('/'.join((base_path, _template)))
            if _template.split('/', 1)[0] == '..':
                log.warning(
                    'Discarded template path "%s": attempts to'
                    ' ascend outside of salt://', template
                )
                raise TemplateNotFound(template)

        self.check_cache(_template)

        if environment and template:
            tpldir = os.path.dirname(_template).replace('\\', '/')
            tplfile = _template
            if is_relative:
                tpldir = environment.globals.get('tpldir', tpldir)
                tplfile = template
            tpldata = {
                'tplfile': tplfile,
                'tpldir': '.' if tpldir == '' else tpldir,
                'tpldot': tpldir.replace('/', '.'),
            }
            environment.globals.update(tpldata)

        # pylint: disable=cell-var-from-loop
        for spath in self.searchpath:
            filepath = os.path.join(spath, _template)
            try:
                with salt.utils.files.fopen(filepath, 'rb') as ifile:
                    contents = ifile.read().decode(self.encoding)
                    mtime = os.path.getmtime(filepath)

                    def uptodate():
                        try:
                            return os.path.getmtime(filepath) == mtime
                        except OSError:
                            return False
                    return contents, filepath, uptodate
            except IOError:
                # there is no file under current path
                continue
        # pylint: enable=cell-var-from-loop

        # there is no template file within searchpaths
        raise TemplateNotFound(template)