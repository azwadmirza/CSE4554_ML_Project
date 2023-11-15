def dump(db, thefile, delimiter=',', **options):
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
        'Byteorder',
        'is signed']
    head_tail = ['Value', 'Name / Phys. Range', 'Function / Increment Unit']

    csvtable = list()  # List holding all csv rows

    col = 0  # Column counter

    # -- headers start:
    headerrow = csvRow()

    # write first row (header) cols before frameardunits:
    for head in head_top:
        headerrow.write(col, head)
        col += 1

    # write frameardunits in first row:
    buList = []
    for bu in db.boardUnits:
        headerrow.write(col, bu.name)
        buList.append(bu.name)
        col += 1

    # write first row (header) cols after frameardunits:
    for head in head_tail:
        headerrow.write(col, head)
        col += 1

    csvtable.append(headerrow)
    # -- headers end...

    frameHash = {}
    for frame in db.frames:
        frameHash[int(frame.id)] = frame

    # set row to first Frame (row = 0 is header)
    row = 1

    # iterate over the frames
    for idx in sorted(frameHash.keys()):
        frame = frameHash[idx]

        # sort signals:
        sigHash = {}
        for sig in frame.signals:
            sigHash["%02d" % int(sig.getStartbit()) + sig.name] = sig

        # iterate over signals
        for sig_idx in sorted(sigHash.keys()):
            sig = sigHash[sig_idx]

            # value table available?
            if sig.values.__len__() > 0:
                # iterate over values in valuetable
                for val in sorted(sig.values.keys()):
                    signalRow = csvRow()
                    writeFramex(frame, signalRow)
                    col = head_top.__len__()
                    col = writeBuMatrixx(buList, sig, frame, signalRow, col)
                    # write Value
                    writeValuex(val, sig.values[val], signalRow, col)
                    writeSignalx(db, sig, signalRow, col)

                    # no min/max here, because min/max has same col as values.
                    # next row
                    row += 1
                    csvtable.append(signalRow)
                # loop over values ends here
            # no value table available
            else:
                signalRow = csvRow()
                writeFramex(frame, signalRow)
                col = head_top.__len__()
                col = writeBuMatrixx(buList, sig, frame, signalRow, col)
                writeSignalx(db, sig, signalRow, col)

                if sig.min is not None or sig.max is not None:
                    signalRow[col + 1] = str("{}..{}".format(sig.min, sig.max))

                # next row
                row += 1
                csvtable.append(signalRow)
                # set style to normal - without border
        # loop over signals ends here
    # loop over frames ends here

    if (sys.version_info > (3, 0)):
        import io
        temp = io.TextIOWrapper(thefile, encoding='UTF-8')
    else:
        temp = thefile

    writer = csv.writer(temp, delimiter=delimiter)
    for row in csvtable:
        writer.writerow(row.as_list)