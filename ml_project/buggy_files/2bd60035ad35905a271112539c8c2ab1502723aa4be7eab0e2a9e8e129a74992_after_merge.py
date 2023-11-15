    def parse_xml(self, source, keep_clark_notation=False):
        """Parses the given XML file or string into an element structure.

        The `source` can either be a path to an XML file or a string containing
        XML. In both cases the XML is parsed into ElementTree
        [http://docs.python.org/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element|element structure]
        and the root element is returned.

        As discussed in `Handling XML namespaces` section, this keyword, by
        default, strips possible namespaces added by ElementTree into tag names.
        This typically eases handling XML documents with namespaces
        considerably. If you do not want that to happen, or want to avoid
        the small overhead of going through the element structure when your
        XML does not have namespaces, you can disable this feature by giving
        `keep_clark_notation` argument a true value (e.g. any non-empty string).

        Examples:
        | ${root} = | Parse XML | <root><child/></root> |
        | ${xml} =  | Parse XML | ${CURDIR}/test.xml    | no namespace cleanup |

        Use `Get Element` keyword if you want to get a certain element and not
        the whole structure. See `Parsing XML` section for more details and
        examples

        Stripping namespaces is a new feature in Robot Framework 2.7.5.
        """
        with ETSource(source) as source:
            root = self.etree.parse(source).getroot()
        if self.lxml_etree:
            self._remove_comments(root)
        if not keep_clark_notation:
            NameSpaceStripper().strip(root)
        return root