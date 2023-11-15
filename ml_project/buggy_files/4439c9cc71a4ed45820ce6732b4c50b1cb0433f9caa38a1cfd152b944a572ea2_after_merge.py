def dump(db, f, **options):
    if 'dbcExportEncoding' in options:
        dbcExportEncoding = options["dbcExportEncoding"]
    else:
        dbcExportEncoding = 'iso-8859-1'
    if 'dbcExportCommentEncoding' in options:
        dbcExportCommentEncoding = options["dbcExportCommentEncoding"]
    else:
        dbcExportCommentEncoding = dbcExportEncoding
    if 'whitespaceReplacement' in options:
        whitespaceReplacement = options["whitespaceReplacement"]
        if whitespaceReplacement in ['', None] or set(
                [' ', '\t']).intersection(whitespaceReplacement):
            print("Warning: Settings may result in whitespace in DBC variable names.  This is not supported by the DBC format.")
    else:
        whitespaceReplacement = '_'
    if 'writeValTable' in options:
        writeValTable = options["writeValTable"]
    else:
        writeValTable = True

    f.write("VERSION \"created by canmatrix\"\n\n".encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    f.write("NS_ :\n\nBS_:\n\n".encode(dbcExportEncoding))

    # Boardunits
    f.write("BU_: ".encode(dbcExportEncoding))
    id = 1
    nodeList = {}
    for bu in db.boardUnits:
        f.write((bu.name + " ").encode(dbcExportEncoding))
    f.write("\n\n".encode(dbcExportEncoding))

    if writeValTable:
        # ValueTables
        for table in db.valueTables:
            f.write(("VAL_TABLE_ " + table).encode(dbcExportEncoding))
            for row in db.valueTables[table]:
                f.write(
                    (' ' +
                     str(row) +
                     ' "' +
                     db.valueTables[table][row] +
                     '"').encode(dbcExportEncoding))
            f.write(";\n".encode(dbcExportEncoding))
        f.write("\n".encode(dbcExportEncoding))

    output_names = collections.defaultdict(dict)

    for frame in db.frames:
        normalized_names = collections.OrderedDict((
            (s, normalizeName(s.name, whitespaceReplacement))
            for s in frame.signals
        ))

        duplicate_signal_totals = collections.Counter(normalized_names.values())
        duplicate_signal_counter = collections.Counter()

        numbered_names = collections.OrderedDict()

        for signal in frame.signals:
            name = normalized_names[signal]
            duplicate_signal_counter[name] += 1
            if duplicate_signal_totals[name] > 1:
                # TODO: pad to 01 in case of 10+ instances, for example?
                name += str(duplicate_signal_counter[name] - 1)

            output_names[frame][signal] = name

    # Frames
    for bo in db.frames:
        multiplex_written = False
        if bo.transmitter.__len__() == 0:
            bo.addTransmitter("Vector__XXX")

        if bo.extended == 1:
            bo.id += 0x80000000
        
        f.write(
            ("BO_ %d " %
             bo.id +
             bo.name +
             ": %d " %
             bo.size +
             bo.transmitter[0] +
             "\n").encode(dbcExportEncoding))
        duplicate_signal_totals = collections.Counter(
            normalizeName(s.name, whitespaceReplacement) for s in bo.signals
        )
        duplicate_signal_counter = collections.Counter()
        for signal in bo.signals:
            if signal.multiplex == 'Multiplexor' and multiplex_written and not bo.is_complex_multiplexed:
                continue

            f.write((" SG_ " + output_names[bo][signal] + " ").encode(dbcExportEncoding))
            if signal.mux_val is not None:
                f.write(("m%d" %
                         int(signal.mux_val)).encode(dbcExportEncoding))
            if signal.multiplex == 'Multiplexor':
                f.write('M'.encode(dbcExportEncoding))
                multiplex_written = True



            startbit = signal.getStartbit(bitNumbering=1)

            if signal.is_signed:
                sign = '-'
            else:
                sign = '+'
            f.write(
                (" : %d|%d@%d%c" %
                 (startbit,
                  signal.signalsize,
                  signal.is_little_endian,
                  sign)).encode(dbcExportEncoding))
            f.write(
                (" (%s,%s)" %
                 (format_float(signal.factor), format_float(signal.offset))).encode(dbcExportEncoding))
            f.write(
                (" [{}|{}]".format(
                    format_float(signal.min),
                    format_float(signal.max))).encode(dbcExportEncoding))
            f.write(' "'.encode(dbcExportEncoding))

            if signal.unit is None:
                signal.unit = ""
            f.write(signal.unit.encode(dbcExportEncoding))
            f.write('" '.encode(dbcExportEncoding))
            if signal.receiver.__len__() == 0:
                signal.addReceiver('Vector__XXX')
            f.write((','.join(signal.receiver) + "\n").encode(dbcExportEncoding))
        f.write("\n".encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    # second Sender:
    for bo in db.frames:
        if bo.transmitter.__len__() > 1:
            f.write(
                ("BO_TX_BU_ %d : %s;\n" %
                 (bo.id, ','.join(
                     bo.transmitter))).encode(dbcExportEncoding))

    # frame comments
    for bo in db.frames:
        if bo.comment is not None and bo.comment.__len__() > 0:
            f.write(
                ("CM_ BO_ " +
                 "%d " %
                 bo.id +
                 ' "').encode(dbcExportEncoding))
            f.write(
                bo.comment.replace(
                    '"',
                    '\\"').encode(dbcExportCommentEncoding, 'ignore'))
            f.write('";\n'.encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    # signal comments
    for bo in db.frames:
        for signal in bo.signals:
            if signal.comment is not None and signal.comment.__len__() > 0:
                name = output_names[bo][signal]
                f.write(
                    ("CM_ SG_ " +
                     "%d " %
                     bo.id +
                     name +
                     ' "').encode(dbcExportEncoding, 'ignore'))
                f.write(
                        signal.comment.replace(
                            '"', '\\"').encode(dbcExportCommentEncoding, 'ignore'))
                f.write('";\n'.encode(dbcExportEncoding, 'ignore'))

    f.write("\n".encode(dbcExportEncoding))

    # boarUnit comments
    for bu in db.boardUnits:
        if bu.comment is not None and bu.comment.__len__() > 0:
            f.write(
                ("CM_ BU_ " +
                 bu.name +
                 ' "' +
                 bu.comment.replace(
                     '"',
                     '\\"') +
                    '";\n').encode(dbcExportCommentEncoding,'ignore'))
    f.write("\n".encode(dbcExportEncoding))

    defaults = {}
    for (dataType, define) in sorted(list(db.frameDefines.items())):
        f.write(
            ('BA_DEF_ BO_ "' +
             dataType +
             '" ').encode(dbcExportEncoding) +
            define.definition.encode(
                dbcExportEncoding,
                'replace') +
            ';\n'.encode(dbcExportEncoding))
        if dataType not in defaults and define.defaultValue is not None:
            defaults[dataType] = define.defaultValue
    for (dataType, define) in sorted(list(db.signalDefines.items())):
        f.write(
            ('BA_DEF_ SG_ "' +
             dataType +
             '" ').encode(dbcExportEncoding) +
            define.definition.encode(
                dbcExportEncoding,
                'replace') +
            ';\n'.encode(dbcExportEncoding))
        if dataType not in defaults and define.defaultValue is not None:
            defaults[dataType] = define.defaultValue
    for (dataType, define) in sorted(list(db.buDefines.items())):
        f.write(
            ('BA_DEF_ BU_ "' +
             dataType +
             '" ').encode(dbcExportEncoding) +
            define.definition.encode(
                dbcExportEncoding,
                'replace') +
            ';\n'.encode(dbcExportEncoding))
        if dataType not in defaults and define.defaultValue is not None:
            defaults[dataType] = define.defaultValue
    for (dataType, define) in sorted(list(db.globalDefines.items())):
        f.write(
            ('BA_DEF_ "' +
             dataType +
             '" ').encode(dbcExportEncoding) +
            define.definition.encode(
                dbcExportEncoding,
                'replace') +
            ';\n'.encode(dbcExportEncoding))
        if dataType not in defaults and define.defaultValue is not None:
            defaults[dataType] = define.defaultValue

    for define in sorted(defaults):
        f.write(
            ('BA_DEF_DEF_ "' +
             define +
             '" ').encode(dbcExportEncoding) +
            defaults[define].encode(
                dbcExportEncoding,
                'replace') +
            ';\n'.encode(dbcExportEncoding))

    # boardunit-attributes:
    for bu in db.boardUnits:
        for attrib, val in sorted(bu.attributes.items()):
            if db.buDefines[attrib].type == "STRING":
                val = '"' + val + '"'
            elif not val:
                val = '""'
            f.write(
                ('BA_ "' +
                 attrib +
                 '" BU_ ' +
                 bu.name +
                 ' ' +
                 str(val) +
                    ';\n').encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    # global-attributes:
    for attrib, val in sorted(db.attributes.items()):
        if db.globalDefines[attrib].type == "STRING":
            val = '"' + val + '"'
        elif not val:
            val = '""'
        f.write(('BA_ "' + attrib + '" ' + val +
                 ';\n').encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    # messages-attributes:
    for frame in db.frames:
        for attrib, val in sorted(frame.attributes.items()):
            if db.frameDefines[attrib].type == "STRING":
               val = '"' + val + '"'
            elif not val:
                val = '""'
            f.write(('BA_ "' + attrib + '" BO_ %d ' %
                     frame.id + val + ';\n').encode(dbcExportEncoding))
    f.write("\n".encode(dbcExportEncoding))

    # signal-attributes:
    for frame in db.frames:
        for signal in frame.signals:
            for attrib, val in sorted(signal.attributes.items()):
                name = output_names[frame][signal]
                if db.signalDefines[attrib].type == "STRING":
                    val = '"' + val + '"'
                elif not val:
                    val = '""'
                elif isinstance(val, float):
                    val = format_float(val)
                f.write(
                    ('BA_ "' +
                     attrib +
                     '" SG_ %d ' %
                     frame.id +
                     name +
                     ' ' +
                     val +
                     ';\n').encode(dbcExportEncoding))
            if signal.is_float:
                if int(signal.signalsize) > 32:
                    f.write(('SIG_VALTYPE_ %d %s : 2;\n' % (frame.id, output_names[bo][signal])).encode(dbcExportEncoding))
                else:
                    f.write(('SIG_VALTYPE_ %d %s : 1;\n' % (frame.id, output_names[bo][signal])).encode(dbcExportEncoding))
 
    f.write("\n".encode(dbcExportEncoding))

    # signal-values:
    for bo in db.frames:
        multiplex_written = False
        for signal in bo.signals:
            if signal.multiplex == 'Multiplexor' and multiplex_written:
                continue

            multiplex_written = True

            if signal.values:
                f.write(
                    ('VAL_ %d ' %
                     bo.id +
                     output_names[bo][signal]).encode(dbcExportEncoding))
                for attrib, val in sorted(
                        signal.values.items(), key=lambda x: int(x[0])):
                    f.write(
                        (' ' + str(attrib) + ' "' + val + '"').encode(dbcExportEncoding))
                f.write(";\n".encode(dbcExportEncoding))

    # signal-groups:
    for bo in db.frames:
        for sigGroup in bo.signalGroups:
            f.write(("SIG_GROUP_ " + str(bo.id) + " " + sigGroup.name +
                     " " + str(sigGroup.id) + " :").encode(dbcExportEncoding))
            for signal in sigGroup.signals:
                f.write((" " + output_names[bo][signal]).encode(dbcExportEncoding))
            f.write(";\n".encode(dbcExportEncoding))

    for frame in db.frames:
        if frame.is_complex_multiplexed:
            for signal in frame.signals:
                if signal.muxerForSignal is not None:
                    f.write(("SG_MUL_VAL_ %d %s %s %d-%d;\n" % (frame.id, signal.name, signal.muxerForSignal, signal.muxValMin, signal.muxValMax)).encode(dbcExportEncoding))