    def run(self):
        """Run listing directive."""
        _fname = self.arguments.pop(0)
        fname = _fname.replace('/', os.sep)
        try:
            lang = self.arguments.pop(0)
            self.options['code'] = lang
        except IndexError:
            self.options['literal'] = True

        if len(self.folders) == 1:
            listings_folder = next(iter(self.folders.keys()))
            if fname.startswith(listings_folder):
                fpath = os.path.join(fname)  # new syntax: specify folder name
            else:
                fpath = os.path.join(listings_folder, fname)  # old syntax: don't specify folder name
        else:
            fpath = os.path.join(fname)  # must be new syntax: specify folder name
        self.arguments.insert(0, fpath)
        if 'linenos' in self.options:
            self.options['number-lines'] = self.options['linenos']
        with io.open(fpath, 'r+', encoding='utf8') as fileobject:
            self.content = fileobject.read().splitlines()
        self.state.document.settings.record_dependencies.add(fpath)
        target = urlunsplit(("link", 'listing', fpath.replace('\\', '/'), '', ''))
        generated_nodes = (
            [core.publish_doctree('`{0} <{1}>`_'.format(_fname, target))[0]])
        generated_nodes += self.get_code_from_file(fileobject)
        return generated_nodes