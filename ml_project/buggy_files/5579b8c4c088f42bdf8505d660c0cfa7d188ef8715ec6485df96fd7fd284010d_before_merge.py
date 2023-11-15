    def gather_elements(self, client, node, style):

        # Take the style from the parent "table" node
        # because sometimes it's not passed down.

        if node.parent['classes']:
            style = client.styles.combinedStyle(['table'] + node.parent['classes'])
        else:
            style = client.styles['table']
        rows = []
        colWidths = []
        hasHead = False
        headRows = 0
        for n in node.children:
            if isinstance(n, docutils.nodes.thead):
                hasHead = True
                for row in n.children:
                    r = []
                    for cell in row.children:
                        r.append(cell)
                    rows.append(r)
                headRows = len(rows)
            elif isinstance(n, docutils.nodes.tbody):
                for row in n.children:
                    r = []
                    for cell in row.children:
                        r.append(cell)
                    rows.append(r)
            elif isinstance(n, docutils.nodes.colspec):
                colWidths.append(int(n['colwidth']))

        # colWidths are in no specific unit, really. Maybe ems.
        # Convert them to %
        colWidths = [int(x) for x in colWidths]
        tot = sum(colWidths)
        colWidths = ["%s%%" % ((100.0 * w) / tot) for w in colWidths]

        if 'colWidths' in style.__dict__:
            colWidths[: len(style.colWidths)] = style.colWidths

        spans = client.filltable(rows)

        data = []
        rowids = range(0, len(rows))
        for row, i in zip(rows, rowids):
            r = []
            j = 0
            for cell in row:
                if isinstance(cell, str):
                    r.append("")
                else:
                    if i < headRows:
                        st = client.styles['table-heading']
                    else:
                        st = client.styles['table-body']
                    ell = client.gather_elements(cell, style=st)
                    r.append(ell)
                j += 1
            data.append(r)

        st = TableStyle(spans)
        if 'commands' in style.__dict__:
            for cmd in style.commands:
                st.add(*cmd)
        else:
            # Only use the commands from "table" if the
            # specified class has no commands.

            for cmd in client.styles['table'].commands:
                st.add(*cmd)

        if hasHead:
            for cmd in client.styles.tstyleHead(headRows):
                st.add(*cmd)
        rtr = client.repeat_table_rows

        t = DelayedTable(data, colWidths, st, rtr)
        if style.alignment == TA_LEFT:
            t.hAlign = 'LEFT'
        elif style.alignment == TA_CENTER:
            t.hAlign = 'CENTER'
        elif style.alignment == TA_RIGHT:
            t.hAlign = 'RIGHT'
        return [t]