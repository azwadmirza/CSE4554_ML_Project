    def _ipython_display_(self):
        try:
            from IPython.display import display
        except ImportError:
            return None

        # Series doesn't define _repr_html_ or _repr_latex_
        latex = self._repr_latex_() if hasattr(self, '_repr_latex_') else None
        html = self._repr_html_() if hasattr(self, '_repr_html_') else None
        try:
            table_schema = self._repr_table_schema_()
        except Exception as e:
            warnings.warn("Cannot create table schema representation. "
                          "{}".format(e), UnserializableWarning)
            table_schema = None
        # We need the inital newline since we aren't going through the
        # usual __repr__. See
        # https://github.com/pandas-dev/pandas/pull/14904#issuecomment-277829277
        text = "\n" + repr(self)

        reprs = {"text/plain": text, "text/html": html, "text/latex": latex,
                 "application/vnd.dataresource+json": table_schema}
        reprs = {k: v for k, v in reprs.items() if v}
        display(reprs, raw=True)