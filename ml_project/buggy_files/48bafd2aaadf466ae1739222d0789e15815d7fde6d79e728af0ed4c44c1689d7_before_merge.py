    def to_xml_file(self, shed_tool_data_table_config, new_elems=None, remove_elems=None):
        """
        Write the current in-memory version of the shed_tool_data_table_conf.xml file to disk.
        remove_elems are removed before new_elems are added.
        """
        if not (new_elems or remove_elems):
            log.debug('ToolDataTableManager.to_xml_file called without any elements to add or remove.')
            return  # no changes provided, no need to persist any changes
        if not new_elems:
            new_elems = []
        if not remove_elems:
            remove_elems = []
        full_path = os.path.abspath(shed_tool_data_table_config)
        # FIXME: we should lock changing this file by other threads / head nodes
        try:
            tree = util.parse_xml(full_path)
            root = tree.getroot()
            out_elems = [elem for elem in root]
        except Exception as e:
            out_elems = []
            log.debug('Could not parse existing tool data table config, assume no existing elements: %s', e)
        for elem in remove_elems:
            # handle multiple occurrences of remove elem in existing elems
            while elem in out_elems:
                remove_elems.remove(elem)
        # add new elems
        out_elems.extend(new_elems)
        out_path_is_new = not os.path.exists(full_path)
        with open(full_path, 'wb') as out:
            out.write('<?xml version="1.0"?>\n<tables>\n')
            for elem in out_elems:
                out.write(util.xml_to_string(elem, pretty=True))
            out.write('</tables>\n')
        os.chmod(full_path, 0o644)
        if out_path_is_new:
            self.tool_data_path_files.update_files()