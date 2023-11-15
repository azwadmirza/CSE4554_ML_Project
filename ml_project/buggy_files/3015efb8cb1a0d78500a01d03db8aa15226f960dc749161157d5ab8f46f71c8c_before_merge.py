    def install_data_managers(self, shed_data_manager_conf_filename, metadata_dict, shed_config_dict,
                              relative_install_dir, repository, repository_tools_tups):
        rval = []
        if 'data_manager' in metadata_dict:
            tpm = tool_panel_manager.ToolPanelManager(self.app)
            repository_tools_by_guid = {}
            for tool_tup in repository_tools_tups:
                repository_tools_by_guid[tool_tup[1]] = dict(tool_config_filename=tool_tup[0], tool=tool_tup[2])
            # Load existing data managers.
            try:
                tree, error_message = xml_util.parse_xml(shed_data_manager_conf_filename, check_exists=False)
            except (OSError, IOError) as exc:
                if exc.errno == errno.ENOENT:
                    with open(shed_data_manager_conf_filename, 'w') as fh:
                        fh.write(SHED_DATA_MANAGER_CONF_XML)
                    tree, error_message = xml_util.parse_xml(shed_data_manager_conf_filename)
                else:
                    raise
            if tree is None:
                return rval
            config_elems = [elem for elem in tree.getroot()]
            repo_data_manager_conf_filename = metadata_dict['data_manager'].get('config_filename', None)
            if repo_data_manager_conf_filename is None:
                log.debug("No data_manager_conf.xml file has been defined.")
                return rval
            data_manager_config_has_changes = False
            relative_repo_data_manager_dir = os.path.join(shed_config_dict.get('tool_path', ''), relative_install_dir)
            repo_data_manager_conf_filename = os.path.join(relative_repo_data_manager_dir, repo_data_manager_conf_filename)
            tree, error_message = xml_util.parse_xml(repo_data_manager_conf_filename)
            if tree is None:
                return rval
            root = tree.getroot()
            for elem in root:
                if elem.tag == 'data_manager':
                    data_manager_id = elem.get('id', None)
                    if data_manager_id is None:
                        log.error("A data manager was defined that does not have an id and will not be installed:\n%s" %
                                  xml_to_string(elem))
                        continue
                    data_manager_dict = metadata_dict['data_manager'].get('data_managers', {}).get(data_manager_id, None)
                    if data_manager_dict is None:
                        log.error("Data manager metadata is not defined properly for '%s'." % (data_manager_id))
                        continue
                    guid = data_manager_dict.get('guid', None)
                    if guid is None:
                        log.error("Data manager guid '%s' is not set in metadata for '%s'." % (guid, data_manager_id))
                        continue
                    elem.set('guid', guid)
                    tool_guid = data_manager_dict.get('tool_guid', None)
                    if tool_guid is None:
                        log.error("Data manager tool guid '%s' is not set in metadata for '%s'." % (tool_guid, data_manager_id))
                        continue
                    tool_dict = repository_tools_by_guid.get(tool_guid, None)
                    if tool_dict is None:
                        log.error("Data manager tool guid '%s' could not be found for '%s'. Perhaps the tool is invalid?" %
                                  (tool_guid, data_manager_id))
                        continue
                    tool = tool_dict.get('tool', None)
                    if tool is None:
                        log.error("Data manager tool with guid '%s' could not be found for '%s'. Perhaps the tool is invalid?" %
                                  (tool_guid, data_manager_id))
                        continue
                    tool_config_filename = tool_dict.get('tool_config_filename', None)
                    if tool_config_filename is None:
                        log.error("Data manager metadata is missing 'tool_config_file' for '%s'." % (data_manager_id))
                        continue
                    elem.set('shed_conf_file', shed_config_dict['config_filename'])
                    if elem.get('tool_file', None) is not None:
                        del elem.attrib['tool_file']  # remove old tool_file info
                    tool_elem = tpm.generate_tool_elem(repository.tool_shed,
                                                       repository.name,
                                                       repository.installed_changeset_revision,
                                                       repository.owner,
                                                       tool_config_filename,
                                                       tool,
                                                       None)
                    elem.insert(0, tool_elem)
                    data_manager = \
                        self.app.data_managers.load_manager_from_elem(elem,
                                                                      tool_path=shed_config_dict.get('tool_path', ''))
                    if data_manager:
                        rval.append(data_manager)
                else:
                    log.warning("Encountered unexpected element '%s':\n%s" % (elem.tag, xml_to_string(elem)))
                config_elems.append(elem)
                data_manager_config_has_changes = True
            # Persist the altered shed_data_manager_config file.
            if data_manager_config_has_changes:
                reload_count = self.app.data_managers._reload_count
                self.data_manager_config_elems_to_xml_file(config_elems, shed_data_manager_conf_filename)
                while self.app.data_managers._reload_count <= reload_count:
                    time.sleep(0.1)  # Wait for shed_data_manager watcher thread to pick up changes
        return rval