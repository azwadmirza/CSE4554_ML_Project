def dump(db, filename, **options):
    if 'xlsMotorolaBitFormat' in options:
        motorolaBitFormat = options["xlsMotorolaBitFormat"]
    else:
        motorolaBitFormat = "msbreverse"

    head_top = [
        'ID',
        'Frame Name',
        'Cycle Time [ms]',
        'Launch Type',
        'Launch Parameter',
        'Signal Byte No.',
        'Signal Bit No.',
        'Signal Name',
        'Signal Function',
        'Signal Length [Bit]',
        'Signal Default',
        ' Signal Not Available',
        'Byteorder']
    head_tail = ['Value', 'Name / Phys. Range', 'Function / Increment Unit']

    workbook = xlsxwriter.Workbook(filename)
#    wsname = os.path.basename(filename).replace('.xlsx', '')
#    worksheet = workbook.add_worksheet('K-Matrix ' + wsname[0:22])
    worksheet = workbook.add_worksheet('K-Matrix ')
    col = 0
    global sty_header
    sty_header = workbook.add_format({'bold': True,
                                      'rotation': 90,
                                      'font_name': 'Verdana',
                                      'font_size': 8,
                                      'align': 'center',
                                      'valign': 'center'})
    global sty_first_frame
    sty_first_frame = workbook.add_format({'font_name': 'Verdana',
                                           'font_size': 8,
                                           'font_color': 'black', 'top': 1})
    global sty_white
    sty_white = workbook.add_format({'font_name': 'Verdana',
                                     'font_size': 8,
                                     'font_color': 'white'})
    global sty_norm
    sty_norm = workbook.add_format({'font_name': 'Verdana',
                                    'font_size': 8,
                                    'font_color': 'black'})

# BUMatrix-Styles
    global sty_green
    sty_green = workbook.add_format({'pattern': 1, 'fg_color': '#CCFFCC'})
    global sty_green_first_frame
    sty_green_first_frame = workbook.add_format(
        {'pattern': 1, 'fg_color': '#CCFFCC', 'top': 1})
    global sty_sender
    sty_sender = workbook.add_format({'pattern': 0x04, 'fg_color': '#C0C0C0'})
    global sty_sender_first_frame
    sty_sender_first_frame = workbook.add_format(
        {'pattern': 0x04, 'fg_color': '#C0C0C0', 'top': 1})
    global sty_sender_green
    sty_sender_green = workbook.add_format(
        {'pattern': 0x04, 'fg_color': '#C0C0C0', 'bg_color': '#CCFFCC'})
    global sty_sender_green_first_frame
    sty_sender_green_first_frame = workbook.add_format(
        {'pattern': 0x04, 'fg_color': '#C0C0C0', 'bg_color': '#CCFFCC', 'top': 1})

    # write first row (header) cols before frameardunits:
    for head in head_top:
        worksheet.write(0, col, head, sty_header)
        worksheet.set_column(col, col, 3.57)
        col += 1

    # write frameardunits in first row:
    buList = []
    for bu in db.boardUnits:
        worksheet.write(0, col, bu.name, sty_header)
        worksheet.set_column(col, col, 3.57)
        buList.append(bu.name)
        col += 1

    head_start = col

    # write first row (header) cols after frameardunits:
    for head in head_tail:
        worksheet.write(0, col, head, sty_header)
        worksheet.set_column(col, col, 6)
        col += 1

    # set width of selected Cols
    worksheet.set_column(0, 0, 3.57)
    worksheet.set_column(1, 1, 21)
    worksheet.set_column(3, 3, 12.29)
    worksheet.set_column(7, 7, 21)
    worksheet.set_column(8, 8, 30)
    worksheet.set_column(head_start + 1, head_start + 1, 21)
    worksheet.set_column(head_start + 2, head_start + 2, 12)

    frameHash = {}
    for frame in db.frames:
        if frame.is_complex_multiplexed:
            logger.error("export complex multiplexers is not supported - ignoring frame " + frame.name)
            continue

        frameHash[int(frame.id)] = frame

    # set row to first Frame (row = 0 is header)
    row = 1

    # iterate over the frames
    for idx in sorted(frameHash.keys()):
        frame = frameHash[idx]
        framestyle = sty_first_frame

        # sort signals:
        sigHash = {}
        for sig in frame.signals:
            sigHash["%02d" % int(sig.getStartbit()) + sig.name] = sig

        # set style for first line with border
        sigstyle = sty_first_frame

        # iterate over signals
        for sig_idx in sorted(sigHash.keys()):
            sig = sigHash[sig_idx]

            # if not first Signal in Frame, set style
            if sigstyle != sty_first_frame:
                sigstyle = sty_norm
            # valuetable available?
            if sig.values.__len__() > 0:
                valstyle = sigstyle
                # iterate over values in valuetable
                for val in sorted(sig.values.keys()):
                    writeFramex(frame, worksheet, row, framestyle)
                    if framestyle != sty_first_frame:
                        worksheet.set_row(row, None, None, {'level': 1})
                    col = head_top.__len__()
                    col = writeBuMatrixx(
                        buList, sig, frame, worksheet, row, col, framestyle)
                    # write Value
                    writeValuex(
                        val,
                        sig.values[val],
                        worksheet,
                        row,
                        col,
                        valstyle)
                    writeSignalx(db, sig, worksheet, row, col,
                                 sigstyle, motorolaBitFormat)

                    # no min/max here, because min/max has same col as values...
                    # next row
                    row += 1
                    # set style to normal - without border
                    sigstyle = sty_white
                    framestyle = sty_white
                    valstyle = sty_norm
                # loop over values ends here
            # no valuetable available
            else:
                writeFramex(frame, worksheet, row, framestyle)
                if framestyle != sty_first_frame:
                    worksheet.set_row(row, None, None, {'level': 1})
                col = head_top.__len__()
                col = writeBuMatrixx(
                    buList, sig, frame, worksheet, row, col, framestyle)
                writeSignalx(db, sig, worksheet, row, col,
                             sigstyle, motorolaBitFormat)

                if float(sig.min) != 0 or float(sig.max) != 1.0:
                    worksheet.write(row, col + 1, str("%g..%g" %
                                                      (sig.min, sig.max)), sigstyle)
                else:
                    worksheet.write(row, col + 1, "", sigstyle)

                # just for border
                worksheet.write(row, col, "", sigstyle)
                # next row
                row += 1
                # set style to normal - without border
                sigstyle = sty_white
                framestyle = sty_white
        # reset signal-Array
        signals = []
        # loop over signals ends here
    # loop over frames ends here

    worksheet.autofilter(0, 0, row, len(head_top) +
                         len(head_tail) + len(db.boardUnits))
    worksheet.freeze_panes(1, 0)
    # save file
    workbook.close()