    def on_finish(self) -> None:
        import lxml.etree as etree

        self.last_xml = None
        # index_path = os.path.join(self.output_dir, 'index.xml')
        output_files = sorted(self.files, key=lambda x: x.module)

        root = etree.Element('mypy-report-index', name=self.main_file)
        doc = etree.ElementTree(root)

        for file_info in output_files:
            etree.SubElement(root, 'file',
                             file_info.attrib(),
                             total=str(file_info.total()),
                             name=file_info.name,
                             module=file_info.module)
        xslt_path = os.path.relpath('mypy-html.xslt', '.')
        transform_pi = etree.ProcessingInstruction('xml-stylesheet',
                'type="text/xsl" href="%s"' % cgi.escape(xslt_path, True))
        root.addprevious(transform_pi)
        self.schema.assertValid(doc)

        self.last_xml = doc