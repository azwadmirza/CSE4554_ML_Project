    def _format_fields(self, fields, title_width=12):
        """Formats a list of fields for display.

        Parameters
        ----------
        fields : list
          A list of 2-tuples: (field_title, field_content)
        title_width : int
          How many characters to pad titles to. Default 12.
        """
        out = []
        header = self.__head
        for title, content in fields:
            if len(content.splitlines()) > 1:
                title = header(title + ":") + "\n"
            else:
                title = header((title+":").ljust(title_width))
            out.append(cast_unicode(title) + cast_unicode(content))
        return "\n".join(out)