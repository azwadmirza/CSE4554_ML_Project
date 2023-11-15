def dump(db, file, **options):
    head_top = ['ID', 'Frame Name', 'Cycle Time [ms]', 'Launch Type', 'Launch Parameter', 'Signal Byte No.', 'Signal Bit No.',
                'Signal Name', 'Signal Function', 'Signal Length [Bit]', 'Signal Default', ' Signal Not Available', 'Byteorder']
    head_tail = ['Value',   'Name / Phys. Range', 'Function / Increment Unit']

    if 'xlsMotorolaBitFormat' in options:
        motorolaBitFormat = options["xlsMotorolaBitFormat"]
    else:
        motorolaBitFormat = "msbreverse"

    workbook = xlwt.Workbook(encoding='utf8')
#    wsname = os.path.basename(filename).replace('.xls', '')
#    worksheet = workbook.add_sheet('K-Matrix ' + wsname[0:22])
    worksheet = workbook.add_sheet('K-Matrix ')
    col = 0

    # write first row (header) cols before frameardunits:
    for head in head_top:
        worksheet.write(0, col, label=head, style=sty_header)
        worksheet.col(col).width = 1111
        col += 1

    # write frameardunits in first row:
    buList = []
    for bu in db.boardUnits:
        worksheet.write(0, col, label=bu.name, style=sty_header)
        worksheet.col(col).width = 1111
        buList.append(bu.name)
        col += 1

    head_start = col

    # write first row (header) cols after frameardunits:
    for head in head_tail:
        worksheet.write(0, col, label=head, style=sty_header)
        worksheet.col(col).width = 3333
        col += 1

    # set width of selected Cols
    worksheet.col(1).width = 5555
    worksheet.col(3).width = 3333
    worksheet.col(7).width = 5555
    worksheet.col(8).width = 7777
    worksheet.col(head_start).width = 1111
    worksheet.col(head_start + 1).width = 5555

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
                    writeFrame(frame, worksheet, row, framestyle)
                    if framestyle != sty_first_frame:
                        worksheet.row(row).level = 1

                    col = head_top.__len__()
                    col = writeBuMatrix(
                        buList, sig, frame, worksheet, row, col, framestyle)
                    # write Value
                    writeValue(
                        val,
                        sig.values[val],
                        worksheet,
                        row,
                        col,
                        valstyle)
                    writeSignal(
                        db,
                        sig,
                        worksheet,
                        row,
                        sigstyle,
                        col,
                        motorolaBitFormat)

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
                writeFrame(frame, worksheet, row, framestyle)
                if framestyle != sty_first_frame:
                    worksheet.row(row).level = 1

                col = head_top.__len__()
                col = writeBuMatrix(
                    buList, sig, frame, worksheet, row, col, framestyle)
                writeSignal(
                    db,
                    sig,
                    worksheet,
                    row,
                    sigstyle,
                    col,
                    motorolaBitFormat)

                if float(sig.min) != 0 or float(sig.max) != 1.0:
                    worksheet.write(
                        row,
                        col +
                        1,
                        label=str(
                            "%g..%g" %
                            (sig.min,
                             sig.max)),
                        style=sigstyle)
                else:
                    worksheet.write(row, col + 1, label="", style=sigstyle)

                # just for border
                worksheet.write(row, col, label="", style=sigstyle)
                # next row
                row += 1
                # set style to normal - without border
                sigstyle = sty_white
                framestyle = sty_white
        # reset signal-Array
        signals = []
        # loop over signals ends here
    # loop over frames ends here

    # frozen headings instead of split panes
    worksheet.set_panes_frozen(True)
    # in general, freeze after last heading row
    worksheet.set_horz_split_pos(1)
    worksheet.set_remove_splits(True)
    # save file
    workbook.save(file)