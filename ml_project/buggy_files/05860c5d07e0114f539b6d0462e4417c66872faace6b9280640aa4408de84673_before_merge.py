def save_html(vd, p, *vsheets):
    'Save vsheets as HTML tables in a single file'

    with open(p, 'w', encoding='ascii', errors='xmlcharrefreplace') as fp:
        for sheet in vsheets:

            fp.write('<h2 class="sheetname">%s</h2>\n'.format(sheetname=html.escape(sheet.name)))

            fp.write('<table id="{sheetname}">\n'.format(sheetname=html.escape(sheet.name)))

            # headers
            fp.write('<tr>')
            for col in sheet.visibleCols:
                contents = html.escape(col.name)
                fp.write('<th>{colname}</th>'.format(colname=contents))
            fp.write('</tr>\n')

            # rows
            with Progress(gerund='saving'):
                for typedvals in sheet.iterdispvals(format=False):
                    fp.write('<tr>')
                    for col, val in typedvals.items():
                        fp.write('<td>')
                        fp.write(html.escape(val))
                        fp.write('</td>')
                    fp.write('</tr>\n')

            fp.write('</table>')
            vd.status('%s save finished' % p)