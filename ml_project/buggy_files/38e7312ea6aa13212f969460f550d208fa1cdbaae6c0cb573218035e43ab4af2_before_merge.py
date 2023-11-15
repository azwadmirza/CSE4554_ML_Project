    def __init__(self, xml_doc, namespace=None):
        """
        Initializes a XMLPaser object.

        :type xml_doc: str, filename, file-like object, parsed XML document
        :param xml_doc: XML document
        :type namespace: str, optional
        :param namespace: Document-wide default namespace. Defaults to ``''``.
        """
        if isinstance(xml_doc, basestring):
            # some string - check if it starts with <?xml
            if xml_doc.strip()[0:5].upper().startswith('<?XML'):
                xml_doc = StringIO.StringIO(xml_doc)
            # parse XML file
            self.xml_doc = etree.parse(xml_doc)
        elif hasattr(xml_doc, 'seek'):
            # some file-based content
            self.xml_doc = etree.parse(xml_doc)
        else:
            self.xml_doc = xml_doc
        self.xml_root = self.xml_doc.getroot()
        self.namespace = namespace or self._getRootNamespace()