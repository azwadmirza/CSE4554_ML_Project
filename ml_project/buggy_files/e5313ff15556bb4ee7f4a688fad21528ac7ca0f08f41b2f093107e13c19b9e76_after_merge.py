    def run(self):

        super(DocCLI, self).run()

        plugin_type = context.CLIARGS['type']

        do_json = context.CLIARGS['json_format']

        if plugin_type in C.DOCUMENTABLE_PLUGINS:
            loader = getattr(plugin_loader, '%s_loader' % plugin_type)
        else:
            raise AnsibleOptionsError("Unknown or undocumentable plugin type: %s" % plugin_type)

        # add to plugin paths from command line
        basedir = context.CLIARGS['basedir']
        if basedir:
            set_collection_playbook_paths(basedir)
            loader.add_directory(basedir, with_subdir=True)
        if context.CLIARGS['module_path']:
            for path in context.CLIARGS['module_path']:
                if path:
                    loader.add_directory(path)

        # save only top level paths for errors
        search_paths = DocCLI.print_paths(loader)
        loader._paths = None  # reset so we can use subdirs below

        # list plugins names and filepath for type
        if context.CLIARGS['list_files']:
            paths = loader._get_paths()
            for path in paths:
                self.plugin_list.update(DocCLI.find_plugins(path, plugin_type))

            plugins = self._get_plugin_list_filenames(loader)
            if do_json:
                jdump(plugins)
            else:
                # format for user
                displace = max(len(x) for x in self.plugin_list)
                linelimit = display.columns - displace - 5
                text = []

                for plugin in plugins.keys():
                    filename = plugins[plugin]
                    text.append("%-*s %-*.*s" % (displace, plugin, linelimit, len(filename), filename))

                DocCLI.pager("\n".join(text))

        # list file plugins for type (does not read docs, very fast)
        elif context.CLIARGS['list_dir']:
            paths = loader._get_paths()
            for path in paths:
                self.plugin_list.update(DocCLI.find_plugins(path, plugin_type))

            descs = self._get_plugin_list_descriptions(loader)
            if do_json:
                jdump(descs)
            else:
                displace = max(len(x) for x in self.plugin_list)
                linelimit = display.columns - displace - 5
                text = []
                deprecated = []
                for plugin in descs.keys():

                    desc = DocCLI.tty_ify(descs[plugin])

                    if len(desc) > linelimit:
                        desc = desc[:linelimit] + '...'

                    if plugin.startswith('_'):  # Handle deprecated
                        deprecated.append("%-*s %-*.*s" % (displace, plugin[1:], linelimit, len(desc), desc))
                    else:
                        text.append("%-*s %-*.*s" % (displace, plugin, linelimit, len(desc), desc))

                    if len(deprecated) > 0:
                        text.append("\nDEPRECATED:")
                        text.extend(deprecated)

                DocCLI.pager("\n".join(text))

        # dump plugin desc/metadata as JSON
        elif context.CLIARGS['dump']:
            plugin_data = {}
            plugin_names = DocCLI.get_all_plugins_of_type(plugin_type)
            for plugin_name in plugin_names:
                plugin_info = DocCLI.get_plugin_metadata(plugin_type, plugin_name)
                if plugin_info is not None:
                    plugin_data[plugin_name] = plugin_info

            jdump(plugin_data)

        else:
            # display specific plugin docs
            if len(context.CLIARGS['args']) == 0:
                raise AnsibleOptionsError("Incorrect options passed")

            # get the docs for plugins in the command line list
            plugin_docs = {}
            for plugin in context.CLIARGS['args']:
                try:
                    doc, plainexamples, returndocs, metadata = DocCLI._get_plugin_doc(plugin, loader, search_paths)
                except PluginNotFound:
                    display.warning("%s %s not found in:\n%s\n" % (plugin_type, plugin, search_paths))
                    continue
                except RemovedPlugin:
                    display.warning("%s %s has been removed\n" % (plugin_type, plugin))
                    continue
                except Exception as e:
                    display.vvv(traceback.format_exc())
                    raise AnsibleError("%s %s missing documentation (or could not parse"
                                       " documentation): %s\n" %
                                       (plugin_type, plugin, to_native(e)))

                if not doc:
                    # The doc section existed but was empty
                    continue

                plugin_docs[plugin] = {'doc': doc, 'examples': plainexamples,
                                       'return': returndocs, 'metadata': metadata}

            if do_json:
                # Some changes to how json docs are formatted
                for plugin, doc_data in plugin_docs.items():
                    try:
                        doc_data['return'] = yaml.load(doc_data['return'])
                    except Exception:
                        pass

                jdump(plugin_docs)

            else:
                # Some changes to how plain text docs are formatted
                text = []
                for plugin, doc_data in plugin_docs.items():
                    textret = DocCLI.format_plugin_doc(plugin, plugin_type,
                                                       doc_data['doc'], doc_data['examples'],
                                                       doc_data['return'], doc_data['metadata'])
                    if textret:
                        text.append(textret)

                if text:
                    DocCLI.pager(''.join(text))

        return 0