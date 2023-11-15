    def _translate(self):
        """
        Convert the DataFrame in `self.data` and the attrs from `_build_styles`
        into a dictionary of {head, body, uuid, cellstyle}
        """
        table_styles = self.table_styles or []
        caption = self.caption
        ctx = self.ctx
        precision = self.precision
        uuid = self.uuid or str(uuid1()).replace("-", "_")
        ROW_HEADING_CLASS = "row_heading"
        COL_HEADING_CLASS = "col_heading"
        DATA_CLASS = "data"
        BLANK_CLASS = "blank"
        BLANK_VALUE = ""

        cell_context = dict()

        n_rlvls = self.data.index.nlevels
        n_clvls = self.data.columns.nlevels
        rlabels = self.data.index.tolist()
        clabels = self.data.columns.tolist()

        idx_values = self.data.index.format(sparsify=False, adjoin=False,
                                            names=False)
        idx_values = lzip(*idx_values)

        if n_rlvls == 1:
            rlabels = [[x] for x in rlabels]
        if n_clvls == 1:
            clabels = [[x] for x in clabels]
        clabels = list(zip(*clabels))

        cellstyle = []
        head = []

        for r in range(n_clvls):
            row_es = [{"type": "th",
                       "value": BLANK_VALUE,
                       "class": " ".join([BLANK_CLASS])}] * n_rlvls
            for c in range(len(clabels[0])):
                cs = [COL_HEADING_CLASS, "level%s" % r, "col%s" % c]
                cs.extend(cell_context.get(
                    "col_headings", {}).get(r, {}).get(c, []))
                value = clabels[r][c]
                row_es.append({"type": "th",
                               "value": value,
                               "display_value": value,
                               "class": " ".join(cs)})
            head.append(row_es)

        if self.data.index.names:
            index_header_row = []

            for c, name in enumerate(self.data.index.names):
                cs = [COL_HEADING_CLASS,
                      "level%s" % (n_clvls + 1),
                      "col%s" % c]
                index_header_row.append({"type": "th", "value": name,
                                         "class": " ".join(cs)})

            index_header_row.extend(
                [{"type": "th",
                  "value": BLANK_VALUE,
                  "class": " ".join([BLANK_CLASS])
                  }] * len(clabels[0]))

            head.append(index_header_row)

        body = []
        for r, idx in enumerate(self.data.index):
            cs = [ROW_HEADING_CLASS, "level%s" % c, "row%s" % r]
            cs.extend(
                cell_context.get("row_headings", {}).get(r, {}).get(c, []))
            row_es = [{"type": "th",
                       "value": rlabels[r][c],
                       "class": " ".join(cs),
                       "display_value": rlabels[r][c]}
                      for c in range(len(rlabels[r]))]

            for c, col in enumerate(self.data.columns):
                cs = [DATA_CLASS, "row%s" % r, "col%s" % c]
                cs.extend(cell_context.get("data", {}).get(r, {}).get(c, []))
                formatter = self._display_funcs[(r, c)]
                value = self.data.iloc[r, c]
                row_es.append({
                    "type": "td",
                    "value": value,
                    "class": " ".join(cs),
                    "id": "_".join(cs[1:]),
                    "display_value": formatter(value)
                })
                props = []
                for x in ctx[r, c]:
                    # have to handle empty styles like ['']
                    if x.count(":"):
                        props.append(x.split(":"))
                    else:
                        props.append(['', ''])
                cellstyle.append({'props': props,
                                  'selector': "row%s_col%s" % (r, c)})
            body.append(row_es)

        return dict(head=head, cellstyle=cellstyle, body=body, uuid=uuid,
                    precision=precision, table_styles=table_styles,
                    caption=caption, table_attributes=self.table_attributes)