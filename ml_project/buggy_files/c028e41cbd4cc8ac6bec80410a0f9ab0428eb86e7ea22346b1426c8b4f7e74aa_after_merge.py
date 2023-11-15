    def write_content(cls, filename, content, rewrite_html=True):
        """Write content to file."""
        if rewrite_html:
            try:
                doc = html.document_fromstring(content)
                doc.rewrite_links(replacer)
                content = html.tostring(doc, encoding='utf8')
            except etree.ParserError:
                content = content.encode('utf-8')
        else:
            content = content.encode('utf-8')

        utils.makedirs(os.path.dirname(filename))
        with open(filename, "wb+") as fd:
            fd.write(content)