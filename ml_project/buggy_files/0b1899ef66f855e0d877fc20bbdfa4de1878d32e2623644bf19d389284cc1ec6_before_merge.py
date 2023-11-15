    def _get_cell_string_value(self, cell) -> str:
        """
        Find and decode OpenDocument text:s tags that represent
        a run length encoded sequence of space characters.
        """
        from odf.element import Element, Text
        from odf.namespaces import TEXTNS
        from odf.text import P, S

        text_p = P().qname
        text_s = S().qname

        p = cell.childNodes[0]

        value = []
        if p.qname == text_p:
            for k, fragment in enumerate(p.childNodes):
                if isinstance(fragment, Text):
                    value.append(fragment.data)
                elif isinstance(fragment, Element):
                    if fragment.qname == text_s:
                        spaces = int(fragment.attributes.get((TEXTNS, "c"), 1))
                    value.append(" " * spaces)
        return "".join(value)