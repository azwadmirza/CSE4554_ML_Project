    def guess_shed_config(self, app):
        tool_ids = []
        for tool in self.metadata.get('tools', []):
            tool_ids.append(tool.get('guid'))
        for shed_tool_conf_dict in app.toolbox.dynamic_confs(include_migrated_tool_conf=True):
            name = shed_tool_conf_dict['config_filename']
            for elem in shed_tool_conf_dict['config_elems']:
                if elem.tag == 'tool':
                    for sub_elem in elem.findall('id'):
                        tool_id = sub_elem.text.strip()
                        if tool_id in tool_ids:
                            self.shed_config_filename = name
                            return shed_tool_conf_dict
                elif elem.tag == "section":
                    for tool_elem in elem.findall('tool'):
                        for sub_elem in tool_elem.findall('id'):
                            tool_id = sub_elem.text.strip()
                            if tool_id in tool_ids:
                                self.shed_config_filename = name
                                return shed_tool_conf_dict
        # We need to search by file paths here, which is less desirable.
        tool_shed = common_util.remove_protocol_and_port_from_tool_shed_url(self.tool_shed)
        for shed_tool_conf_dict in app.toolbox.dynamic_confs(include_migrated_tool_conf=True):
            tool_path = shed_tool_conf_dict['tool_path']
            relative_path = os.path.join(tool_path, tool_shed, 'repos', self.owner, self.name)
            if os.path.exists(relative_path):
                self.shed_config_filename = shed_tool_conf_dict['config_filename']
                return shed_tool_conf_dict
        return {}