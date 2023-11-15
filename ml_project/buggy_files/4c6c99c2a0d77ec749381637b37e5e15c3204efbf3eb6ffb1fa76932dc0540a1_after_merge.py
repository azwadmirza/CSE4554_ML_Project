    def handle_page(self, pagename, addctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """Create a rendered page.

        This method is overwritten for genindex pages in order to fix href link
        attributes.
        """
        if pagename.startswith('genindex') and 'genindexentries' in addctx:
            if not self.use_index:
                return
            self.fix_genindex(addctx['genindexentries'])
        addctx['doctype'] = self.doctype
        StandaloneHTMLBuilder.handle_page(self, pagename, addctx, templatename,
                                          outfilename, event_arg)