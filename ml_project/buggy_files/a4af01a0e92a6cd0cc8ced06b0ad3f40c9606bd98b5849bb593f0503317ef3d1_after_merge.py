    def _write_integrated_tool_panel_config_file( self ):
        """
        Write the current in-memory version of the integrated_tool_panel.xml file to disk.  Since Galaxy administrators
        use this file to manage the tool panel, we'll not use xml_to_string() since it doesn't write XML quite right.
        """
        tracking_directory = self._integrated_tool_panel_tracking_directory
        if not tracking_directory:
            fd, filename = tempfile.mkstemp()
        else:
            if not os.path.exists(tracking_directory):
                os.makedirs(tracking_directory)
            name = "integrated_tool_panel_%.10f.xml" % time.time()
            filename = os.path.join(tracking_directory, name)
            open_file = open(filename, "w")
            fd = open_file.fileno()
        os.write( fd, '<?xml version="1.0"?>\n' )
        os.write( fd, '<toolbox>\n' )
        os.write( fd, '    <!--\n    ')
        os.write( fd, '\n    '.join( [ l for l in INTEGRATED_TOOL_PANEL_DESCRIPTION.split("\n") if l ] ) )
        os.write( fd, '\n    -->\n')
        for key, item_type, item in self._integrated_tool_panel.panel_items_iter():
            if item:
                if item_type == panel_item_types.TOOL:
                    os.write( fd, '    <tool id="%s" />\n' % item.id )
                elif item_type == panel_item_types.WORKFLOW:
                    os.write( fd, '    <workflow id="%s" />\n' % item.id )
                elif item_type == panel_item_types.LABEL:
                    label_id = item.id or ''
                    label_text = item.text or ''
                    label_version = item.version or ''
                    os.write( fd, '    <label id="%s" text="%s" version="%s" />\n' % ( label_id, label_text, label_version ) )
                elif item_type == panel_item_types.SECTION:
                    section_id = item.id or ''
                    section_name = item.name or ''
                    section_version = item.version or ''
                    os.write( fd, '    <section id="%s" name="%s" version="%s">\n' % ( escape(section_id), escape(section_name), section_version ) )
                    for section_key, section_item_type, section_item in item.panel_items_iter():
                        if section_item_type == panel_item_types.TOOL:
                            if section_item:
                                os.write( fd, '        <tool id="%s" />\n' % section_item.id )
                        elif section_item_type == panel_item_types.WORKFLOW:
                            if section_item:
                                os.write( fd, '        <workflow id="%s" />\n' % section_item.id )
                        elif section_item_type == panel_item_types.LABEL:
                            if section_item:
                                label_id = section_item.id or ''
                                label_text = section_item.text or ''
                                label_version = section_item.version or ''
                                os.write( fd, '        <label id="%s" text="%s" version="%s" />\n' % ( label_id, label_text, label_version ) )
                    os.write( fd, '    </section>\n' )
        os.write( fd, '</toolbox>\n' )
        os.close( fd )
        destination = os.path.abspath( self._integrated_tool_panel_config )
        if tracking_directory:
            open(filename + ".stack", "w").write(''.join(traceback.format_stack()))
            shutil.copy( filename, filename + ".copy" )
            filename = filename + ".copy"
        shutil.move( filename, destination )
        os.chmod( self._integrated_tool_panel_config, 0o644 )