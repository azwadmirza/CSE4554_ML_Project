    def execute_searches(self, config, entries, task):
        """
        :param config: Discover plugin config
        :param entries: List of pseudo entries to search
        :param task: Task being run
        :return: List of entries found from search engines listed under `from` configuration
        """

        result = []
        for index, entry in enumerate(entries):
            entry_results = []
            for item in config['from']:
                if isinstance(item, dict):
                    plugin_name, plugin_config = list(item.items())[0]
                else:
                    plugin_name, plugin_config = item, None
                search = get_plugin_by_name(plugin_name).instance
                if not callable(getattr(search, 'search')):
                    log.critical('Search plugin %s does not implement search method', plugin_name)
                    continue
                log.verbose('Searching for `%s` with plugin `%s` (%i of %i)', entry['title'], plugin_name, index + 1,
                            len(entries))
                try:
                    search_results = search.search(task=task, entry=entry, config=plugin_config)
                    if not search_results:
                        log.debug('No results from %s', plugin_name)
                        continue
                    log.debug('Discovered %s entries from %s', len(search_results), plugin_name)
                    if config.get('limit'):
                        search_results = sorted(search_results, reverse=True,
                                                key=lambda x: x.get('search_sort', ''))[:config['limit']]
                    for e in search_results:
                        e['discovered_from'] = entry['title']
                        e['discovered_with'] = plugin_name
                        # 'search_results' can be any iterable, make sure it's a list.
                        e.on_complete(self.entry_complete, query=entry, search_results=list(search_results))

                    entry_results.extend(search_results)

                except PluginWarning as e:
                    log.verbose('No results from %s: %s', plugin_name, e)
                except PluginError as e:
                    log.error('Error searching with %s: %s', plugin_name, e)
            if not entry_results:
                log.verbose('No search results for `%s`', entry['title'])
                entry.complete()
                continue
            result.extend(entry_results)

        return sorted(result, reverse=True, key=lambda x: x.get('search_sort', -1))