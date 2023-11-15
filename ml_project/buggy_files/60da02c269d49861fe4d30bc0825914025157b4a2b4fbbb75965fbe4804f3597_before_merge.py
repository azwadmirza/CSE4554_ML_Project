    def on_file(self, tree: MypyFile, type_map: Dict[Node, Type]) -> None:
        import lxml.etree as etree

        self.last_xml = None
        path = os.path.relpath(tree.path)
        if stats.is_special_module(path):
            return
        if path.startswith('..'):
            return
        if 'stubs' in path.split('/'):
            return

        visitor = stats.StatisticsVisitor(inferred=True, typemap=type_map, all_nodes=True)
        tree.accept(visitor)

        root = etree.Element('mypy-report-file', name=path, module=tree._fullname)
        doc = etree.ElementTree(root)
        file_info = FileInfo(path, tree._fullname)

        with open(path) as input_file:
            for lineno, line_text in enumerate(input_file, 1):
                status = visitor.line_map.get(lineno, stats.TYPE_EMPTY)
                file_info.counts[status] += 1
                etree.SubElement(root, 'line',
                                 number=str(lineno),
                                 precision=stats.precision_names[status],
                                 content=line_text[:-1])
        # Assumes a layout similar to what XmlReporter uses.
        xslt_path = os.path.relpath('mypy-html.xslt', path)
        xml_pi = etree.ProcessingInstruction('xml', 'version="1.0" encoding="utf-8"')
        transform_pi = etree.ProcessingInstruction('xml-stylesheet',
                'type="text/xsl" href="%s"' % cgi.escape(xslt_path, True))
        root.addprevious(xml_pi)
        root.addprevious(transform_pi)
        self.schema.assertValid(doc)

        self.last_xml = doc
        self.files.append(file_info)