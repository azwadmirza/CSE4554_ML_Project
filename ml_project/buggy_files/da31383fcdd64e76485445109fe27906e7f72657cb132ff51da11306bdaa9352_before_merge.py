    def run(self):

        super(DocCLI, self).run()

        plugin_type = self.options.type

        # choose plugin type
        if plugin_type == 'cache':
            loader = cache_loader
        elif plugin_type == 'callback':
            loader = callback_loader
        elif plugin_type == 'connection':
            loader = connection_loader
        elif plugin_type == 'lookup':
            loader = lookup_loader
        elif plugin_type == 'strategy':
            loader = strategy_loader
        elif plugin_type == 'vars':
            loader = vars_loader
        elif plugin_type == 'inventory':
            loader = PluginLoader('InventoryModule', 'ansible.plugins.inventory', 'inventory_plugins', 'inventory_plugins')
        else:
            loader = module_loader

        # add to plugin path from command line
        if self.options.module_path is not None:
            for i in self.options.module_path.split(os.pathsep):
                loader.add_directory(i)

        # save only top level paths for errors
        search_paths = DocCLI.print_paths(loader)
        loader._paths = None  # reset so we can use subdirs below

        # list plugins for type
        if self.options.list_dir:
            paths = loader._get_paths()
            for path in paths:
                self.find_plugins(path, plugin_type)

            self.pager(self.get_plugin_list_text(loader))
            return 0

        # process all plugins of type
        if self.options.all_plugins:
            paths = loader._get_paths()
            for path in paths:
                self.find_plugins(path, plugin_type)
            self.args = sorted(set(self.plugin_list))

        if len(self.args) == 0:
            raise AnsibleOptionsError("Incorrect options passed")

        # process command line list
        text = ''
        for plugin in self.args:

            try:
                # if the plugin lives in a non-python file (eg, win_X.ps1), require the corresponding python file for docs
                filename = loader.find_plugin(plugin, mod_type='.py', ignore_deprecated=True, check_aliases=True)
                if filename is None:
                    display.warning("%s %s not found in:\n%s\n" % (plugin_type, plugin, search_paths))
                    continue

                if any(filename.endswith(x) for x in C.BLACKLIST_EXTS):
                    continue

                try:
                    doc, plainexamples, returndocs, metadata = plugin_docs.get_docstring(filename, verbose=(self.options.verbosity > 0))
                except:
                    display.vvv(traceback.format_exc())
                    display.error("%s %s has a documentation error formatting or is missing documentation." % (plugin_type, plugin))
                    continue

                if doc is not None:

                    # assign from other sections
                    doc['plainexamples'] = plainexamples
                    doc['returndocs'] = returndocs
                    doc['metadata'] = metadata

                    # generate extra data
                    if plugin_type == 'module':
                        # is there corresponding action plugin?
                        if plugin in action_loader:
                            doc['action'] = True
                        else:
                            doc['action'] = False
                    doc['filename'] = filename
                    doc['now_date'] = datetime.date.today().strftime('%Y-%m-%d')
                    if 'docuri' in doc:
                        doc['docuri'] = doc[plugin_type].replace('_', '-')

                    if self.options.show_snippet and plugin_type == 'module':
                        text += self.get_snippet_text(doc)
                    else:
                        text += self.get_man_text(doc)
                else:
                    # this typically means we couldn't even parse the docstring, not just that the YAML is busted,
                    # probably a quoting issue.
                    raise AnsibleError("Parsing produced an empty object.")
            except Exception as e:
                display.vvv(traceback.format_exc())
                raise AnsibleError("%s %s missing documentation (or could not parse documentation): %s\n" % (plugin_type, plugin, str(e)))

        if text:
            self.pager(text)
        return 0