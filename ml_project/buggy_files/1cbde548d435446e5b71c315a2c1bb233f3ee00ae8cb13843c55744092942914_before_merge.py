    def psource(self,obj,oname=''):
        """Print the source code for an object."""

        # Flush the source cache because inspect can return out-of-date source
        linecache.checkcache()
        try:
            src = getsource(obj)
        except:
            self.noinfo('source',oname)
        else:
            page.page(self.format(py3compat.unicode_to_str(src)))