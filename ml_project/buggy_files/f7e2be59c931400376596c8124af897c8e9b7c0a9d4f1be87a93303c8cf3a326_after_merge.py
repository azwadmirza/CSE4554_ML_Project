    def set_table_styles(self, table_styles):
        """
        Set the table styles on a Styler. These are placed in a
        ``<style>`` tag before the generated HTML table.

        .. versionadded:: 0.17.1

        Parameters
        ----------
        table_styles: list
            Each individual table_style should be a dictionary with
            ``selector`` and ``props`` keys. ``selector`` should be a CSS
            selector that the style will be applied to (automatically
            prefixed by the table's UUID) and ``props`` should be a list of
            tuples with ``(attribute, value)``.

        Returns
        -------
        self : Styler

        Examples
        --------
        >>> df = pd.DataFrame(np.random.randn(10, 4))
        >>> df.style.set_table_styles(
        ...     [{'selector': 'tr:hover',
        ...       'props': [('background-color', 'yellow')]}]
        ... )
        """
        self.table_styles = table_styles
        return self