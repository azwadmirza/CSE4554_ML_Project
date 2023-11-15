def dump(db, f, **options):
    if 'dbfExportEncoding' in options:
        dbfExportEncoding = options["dbfExportEncoding"]
    else:
        dbfExportEncoding = 'iso-8859-1'

    outstr =  """//******************************BUSMASTER Messages and signals Database ******************************//

[DATABASE_VERSION] 1.3

[PROTOCOL] CAN

[BUSMASTER_VERSION] [1.7.2]
[NUMBER_OF_MESSAGES] """

    outstr += str(len(db.frames)) + "\n"

    # Frames
    for frame in db.frames:
        # Name unMsgId m_ucLength m_ucNumOfSignals m_cDataFormat m_cFrameFormat? m_txNode
        # m_cDataFormat If 1 dataformat Intel, 0- Motorola -- immer 1 original Converter macht das nach anzahl entsprechender Signale
        # cFrameFormat Standard 'S' Extended 'X'
        extended = 'S'
        if frame.extended == 1:
            extended = 'X'
        outstr += "[START_MSG] " + frame.name + \
            ",%d,%d,%d,1,%c," % (frame.id, frame.size,
                                 len(frame.signals), extended)
        if frame.transmitter.__len__() == 0:
            frame.addTransmitter("Vector__XXX")
# DBF does not support multiple Transmitters
        outstr += frame.transmitter[0] + "\n"

        for signal in frame.signals:
            # m_acName ucLength m_ucWhichByte m_ucStartBit
            # m_ucDataFormat m_fOffset m_fScaleFactor m_acUnit m_acMultiplex m_rxNode
            # m_ucDataFormat
            whichbyte = int(
                math.floor(
                    signal.getStartbit(
                        bitNumbering=1,
                        startLittle=True) /
                    8) +
                1)
            sign = 'S'

            if not signal.is_signed:
                sign = 'U'
            
            if signal.is_float:
                if signal.signalsize > 32:
                    sign = 'D'
                else:
                    sign = 'F'

            if signal.factor == 0:
                signal.factor = 1

            outstr += "[START_SIGNALS] " + signal.name + ",%d,%d,%d,%c," % (signal.signalsize,
                                                                            whichbyte,
                                                                            int(signal.getStartbit(bitNumbering=1,
                                                                                                   startLittle=True)) % 8,
                                                                            sign) + '{},{}'.format(float(signal.max) / float(signal.factor),
                                                                                                   float(signal.min) / float(signal.factor))

            outstr += ",%d,%s,%s" % (signal.is_little_endian,
                                     signal.offset, signal.factor)
            multiplex = ""
            if signal.multiplex is not None:
                if signal.multiplex == 'Multiplexor':
                    multiplex = 'M'
                else:
                    multiplex = 'm' + str(signal.multiplex)

            outstr += "," + signal.unit + ",%s," % multiplex + \
                ','.join(signal.receiver) + "\n"

            if len(signal.values) > 0:
                for attrib, val in sorted(list(signal.values.items())):
                    outstr += '[VALUE_DESCRIPTION] "' + \
                        val + '",' + str(attrib) + '\n'

        outstr += "[END_MSG]\n\n"

    # Boardunits
    outstr += "[NODE] "
    count = 1
    for bu in db.boardUnits:
        outstr += bu.name
        if count < len(db.boardUnits):
            outstr += ","
        count += 1
    outstr += "\n"

    outstr += "[START_DESC]\n\n"

    # BU-descriptions
    outstr += "[START_DESC_MSG]\n"
    for frame in db.frames:
        if frame.comment is not None:
            comment = frame.comment.replace("\n", " ")
            outstr += str(frame.id) + ' S "' + comment + '";\n'

    outstr += "[END_DESC_MSG]\n"

    # Frame descriptions
    outstr += "[START_DESC_NODE]\n"
    for bu in db.boardUnits:
        if bu.comment is not None:
            comment = bu.comment.replace("\n", " ")
            outstr += bu.name + ' "' + comment + '";\n'

    outstr += "[END_DESC_NODE]\n"

    # signal descriptions
    outstr += "[START_DESC_SIG]\n"
    for frame in db.frames:
        for signal in frame.signals:
            if signal.comment is not None:
                comment = signal.comment.replace("\n", " ")
                outstr += "%d S " % frame.id + signal.name + ' "' + comment + '";\n'

    outstr += "[END_DESC_SIG]\n"
    outstr += "[END_DESC]\n\n"

    outstr += "[START_PARAM]\n"
    # db-parameter
    outstr += "[START_PARAM_NET]\n"
    for (type, define) in list(db.globalDefines.items()):
        defaultVal = define.defaultValue
        if defaultVal is None:
            defaultVal = "0"
        outstr += '"' + type + '",' + define.definition.replace(' ', ',') + ',' + defaultVal + '\n'
    outstr += "[END_PARAM_NET]\n"

    # bu-parameter
    outstr += "[START_PARAM_NODE]\n"
    for (type, define) in list(db.buDefines.items()):
        defaultVal = define.defaultValue
        if defaultVal is None:
            defaultVal = "0"
        outstr += '"' + type + '",' + define.definition.replace(' ', ',') + ',' + defaultVal + '\n'
    outstr += "[END_PARAM_NODE]\n"

    # frame-parameter
    outstr += "[START_PARAM_MSG]\n"
    for (type, define) in list(db.frameDefines.items()):
        defaultVal = define.defaultValue
        if defaultVal is None:
            defaultVal = "0"
        outstr += '"' + type + '",' + define.definition.replace(' ', ',') + ',' + defaultVal + '\n'

    outstr += "[END_PARAM_MSG]\n"

    # signal-parameter
    outstr += "[START_PARAM_SIG]\n"
    for (type, define) in list(db.signalDefines.items()):
        defaultVal = define.defaultValue
        if defaultVal is None:
            defaultVal = "0"
        outstr += '"' + type + '",' + define.definition.replace(' ', ',') + ',' + defaultVal + '\n'
    outstr += "[END_PARAM_SIG]\n"

    outstr += "[START_PARAM_VAL]\n"
    # boardunit-attributes:
    outstr += "[START_PARAM_NODE_VAL]\n"
    for bu in db.boardUnits:
        for attrib, val in sorted(list(bu.attributes.items())):
            outstr += bu.name + ',"' + attrib + '","' + val + '"\n'
    outstr += "[END_PARAM_NODE_VAL]\n"

    # messages-attributes:
    outstr += "[START_PARAM_MSG_VAL]\n"
    for frame in db.frames:
        for attrib, val in sorted(list(frame.attributes.items())):
            outstr += str(frame.id) + ',S,"' + attrib + '","' + val + '"\n'
    outstr += "[END_PARAM_MSG_VAL]\n"

    # signal-attributes:
    outstr += "[START_PARAM_SIG_VAL]\n"
    for frame in db.frames:
        for signal in frame.signals:
            for attrib, val in sorted(list(signal.attributes.items())):
                outstr += str(frame.id) + ',S,' + signal.name + \
                    ',"' + attrib + '","' + val + '"\n'
    outstr += "[END_PARAM_SIG_VAL]\n"
    outstr += "[END_PARAM_VAL]\n"
    f.write(outstr.encode(dbfExportEncoding))