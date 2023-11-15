    def _as_table(self, i1, i2, j1=None, j2=None, format='html'):
        from .formatting import _format_value
        parts = []  # """<div>%s (length=%d)</div>""" % (self.name, len(self))]
        parts += ["<table class='table-striped'>"]

        aliases_reverse = {value: key for key, value in self._column_aliases.items()}
        column_names = self.get_column_names()
        values_list = []
        values_list.append(['#', []])
        # parts += ["<thead><tr>"]
        for name in column_names:
            values_list.append([aliases_reverse.get(name, name), []])
            # parts += ["<th>%s</th>" % name]
        # parts += ["</tr></thead>"]

        def table_part(k1, k2, parts):
            N = k2 - k1
            # slicing will invoke .extract which will make the evaluation
            # much quicker
            df = self[k1:k2]
            try:
                values = dict(zip(column_names, df.evaluate(column_names)))
            except:
                values = {}
                for i, name in enumerate(column_names):
                    try:
                        values[name] = df.evaluate(name)
                    except:
                        values[name] = ["error"] * (N)
                        logger.exception('error evaluating: %s at rows %i-%i' % (name, k1, k2))
            for i in range(k2 - k1):
                # parts += ["<tr>"]
                # parts += ["<td><i style='opacity: 0.6'>{:,}</i></td>".format(i + k1)]
                if format == 'html':
                    value = "<i style='opacity: 0.6'>{:,}</i>".format(i + k1)
                else:
                    value = "{:,}".format(i + k1)
                values_list[0][1].append(value)
                for j, name in enumerate(column_names):
                    value = values[name][i]
                    value = _format_value(value)
                    values_list[j+1][1].append(value)
                # parts += ["</tr>"]
            # return values_list
        if i2 - i1 > 0:
            parts = table_part(i1, i2, parts)
            if j1 is not None and j2 is not None:
                values_list[0][1].append('...')
                for i in range(len(column_names)):
                    # parts += ["<td>...</td>"]
                    values_list[i+1][1].append('...')

                # parts = table_part(j1, j2, parts)
                table_part(j1, j2, parts)
        else:
            for header, values in values_list:
                values.append(None)
        # parts += "</table>"
        # html = "".join(parts)
        # return html
        values_list = dict(values_list)
        # print(values_list)
        import tabulate
        table_text = tabulate.tabulate(values_list, headers="keys", tablefmt=format)
        if i2 - i1 == 0:
            if self._length_unfiltered != len(self):
                footer_text = 'No rows to display (because of filtering).'
            else:
                footer_text = 'No rows to display.'
            if format == 'html':
                table_text += f'<i>{footer_text}</i>'
            if format == 'plain':
                table_text += f'\n{footer_text}'
        return table_text