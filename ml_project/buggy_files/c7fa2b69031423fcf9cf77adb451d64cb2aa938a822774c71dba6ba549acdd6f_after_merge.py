def dump(mydb, f, **options):
    # type: (canmatrix.CanMatrix, typing.IO, **typing.Any) -> None
    # create copy because export changes database
    db = copy.deepcopy(mydb)
    dbf_export_encoding = options.get("dbfExportEncoding", 'iso-8859-1')
    ignore_encoding_errors = options.get("ignoreEncodingErrors", "strict")
    db.enum_attribs_to_keys()
    if len(db.signals) > 0:
        free_signals_dummy_frame = canmatrix.Frame("VECTOR__INDEPENDENT_SIG_MSG")
        free_signals_dummy_frame.arbitration_id = canmatrix.ArbitrationId(id=0x40000000, extended=True)
        free_signals_dummy_frame.signals = db.signals
        db.add_frame(free_signals_dummy_frame)

    out_str = """//******************************BUSMASTER Messages and signals Database ******************************//

[DATABASE_VERSION] 1.3

[PROTOCOL] CAN

[BUSMASTER_VERSION] [1.7.2]
[NUMBER_OF_MESSAGES] """

    out_str += str(len(db.frames)) + "\n"

    cycle_times_of_all_frames = [x.cycle_time for x in db.frames]
    if len(cycle_times_of_all_frames) > 0 and max(cycle_times_of_all_frames ) > 0:
        db.add_frame_defines("GenMsgCycleTime", 'INT 0 65535')

    cycle_times_of_all_singals = [x.cycle_time for y in db.frames for x in y.signals]
    if len(cycle_times_of_all_singals) > 0 and max(cycle_times_of_all_singals) > 0:
        db.add_signal_defines("GenSigCycleTime", 'INT 0 65535')

    initial_values_of_all_singals = [x.initial_value for y in db.frames for x in y.signals]
    if len(initial_values_of_all_singals) > 0 and (max(initial_values_of_all_singals) > 0 or min(initial_values_of_all_singals)) < 0:
        db.add_signal_defines("GenSigStartValue", 'FLOAT 0 100000000000')

    # Frames
    for frame in db.frames:
        if frame.is_complex_multiplexed:
            logger.error("export complex multiplexers is not supported - ignoring frame " + frame.name)
            continue

        # Name unMsgId m_ucLength m_ucNumOfSignals m_cDataFormat m_cFrameFormat? m_txNode
        # m_cDataFormat Data format: 1-Intel, 0-Motorola -- always 1 original converter decides based on signal count.
        # cFrameFormat Standard 'S' Extended 'X'
        extended = 'X' if frame.arbitration_id.extended == 1 else 'S'
        out_str += "[START_MSG] " + frame.name + \
            ",%d,%d,%d,1,%c," % (frame.arbitration_id.id, frame.size, len(frame.signals), extended)
        if not frame.transmitters:
            frame.add_transmitter("Vector__XXX")
# DBF does not support multiple Transmitters
        out_str += frame.transmitters[0] + "\n"

        for signal in frame.signals:
            # m_acName ucLength m_ucWhichByte m_ucStartBit
            # m_ucDataFormat m_fOffset m_fScaleFactor m_acUnit m_acMultiplex m_rxNode
            # m_ucDataFormat
            which_byte = int(
                math.floor(
                    signal.get_startbit(
                        bit_numbering=1,
                        start_little=True) /
                    8) +
                1)
            sign = 'I'

            if not signal.is_signed:
                sign = 'U'
            
            if signal.is_float:
                if signal.size > 32:
                    sign = 'D'
                else:
                    sign = 'F'

            if signal.factor == 0:
                signal.factor = 1

            out_str += "[START_SIGNALS] " + signal.name \
                       + ",%d,%d,%d,%c," % (signal.size,
                                            which_byte,
                                            int(signal.get_startbit(bit_numbering=1,
                                                                    start_little=True)) % 8,
                                            sign) + '{},{}'.format(float(signal.max) / float(signal.factor),
                                                                   float(signal.min) / float(signal.factor))

            out_str += ",%d,%s,%s" % (signal.is_little_endian, signal.offset, signal.factor)
            multiplex = ""
            if signal.multiplex is not None:
                if signal.multiplex == 'Multiplexor':
                    multiplex = 'M'
                else:
                    multiplex = 'm' + str(signal.multiplex)

            out_str += "," + signal.unit + ",%s," % multiplex + \
                ','.join(signal.receivers) + "\n"

            if len(signal.values) > 0:
                for value, name in sorted(list(signal.values.items())):
                    out_str += '[VALUE_DESCRIPTION] "' + \
                        name + '",' + str(value) + '\n'

        out_str += "[END_MSG]\n\n"

    # Board units
    out_str += "[NODE] "
    count = 1
    for ecu in db.ecus:
        out_str += ecu.name
        if count < len(db.ecus):
            out_str += ","
        count += 1
    out_str += "\n"

    out_str += "[START_DESC]\n\n"

    # BU-descriptions
    out_str += "[START_DESC_MSG]\n"
    for frame in db.frames:
        if frame.comment is not None:
            comment = frame.comment.replace("\n", " ")
            out_str += str(frame.arbitration_id.id) + ' S "' + comment + '";\n'

    out_str += "[END_DESC_MSG]\n"

    # Frame descriptions
    out_str += "[START_DESC_NODE]\n"
    for ecu in db.ecus:
        if ecu.comment is not None:
            comment = ecu.comment.replace("\n", " ")
            out_str += ecu.name + ' "' + comment + '";\n'

    out_str += "[END_DESC_NODE]\n"

    # signal descriptions
    out_str += "[START_DESC_SIG]\n"
    for frame in db.frames:
        if frame.is_complex_multiplexed:
            continue

        for signal in frame.signals:
            if signal.comment is not None:
                comment = signal.comment.replace("\n", " ")
                out_str += "%d S " % frame.arbitration_id.id + signal.name + ' "' + comment + '";\n'

    out_str += "[END_DESC_SIG]\n"
    out_str += "[END_DESC]\n\n"

    out_str += "[START_PARAM]\n"

    # db-parameter
    out_str += "[START_PARAM_NET]\n"
    for (data_type, define) in sorted(list(db.global_defines.items())):
        default_val = define.defaultValue
        if default_val is None:
            default_val = "0"
        out_str += '"' + data_type + '",' + define.definition.replace(' ', ',') + ',' + default_val + '\n'
    out_str += "[END_PARAM_NET]\n"

    # bu-parameter
    out_str += "[START_PARAM_NODE]\n"
    for (data_type, define) in sorted(list(db.ecu_defines.items())):
        default_val = define.defaultValue
        if default_val is None:
            default_val = "0"
        out_str += '"' + data_type + '",' + define.definition.replace(' ', ',') + ',' + default_val + '\n'
    out_str += "[END_PARAM_NODE]\n"

    # frame-parameter
    out_str += "[START_PARAM_MSG]\n"
    for (data_type, define) in sorted(list(db.frame_defines.items())):
        default_val = define.defaultValue
        if default_val is None:
            default_val = "0"
        out_str += '"' + data_type + '",'  + define.definition.replace(' ', ',') + '\n'  # + ',' + default_val + '\n'

    out_str += "[END_PARAM_MSG]\n"

    # signal-parameter
    out_str += "[START_PARAM_SIG]\n"
    for (data_type, define) in list(db.signal_defines.items()):
        default_val = define.defaultValue
        if default_val is None:
            default_val = "0"
        out_str += '"' + data_type + '",' + define.definition.replace(' ', ',') + ',' + default_val + '\n'
    out_str += "[END_PARAM_SIG]\n"

    out_str += "[START_PARAM_VAL]\n"
    # board unit attributes:
    out_str += "[START_PARAM_NODE_VAL]\n"
    for ecu in db.ecus:
        for attrib, val in sorted(list(ecu.attributes.items())):
            out_str += ecu.name + ',"' + attrib + '","' + val + '"\n'
    out_str += "[END_PARAM_NODE_VAL]\n"

    # messages-attributes:
    out_str += "[START_PARAM_MSG_VAL]\n"
    for frame in db.frames:
        if frame.is_complex_multiplexed:
            continue

        for attrib, val in sorted(list(frame.attributes.items())):
            out_str += str(frame.arbitration_id.id) + ',S,"' + attrib + '","' + val + '"\n'
    out_str += "[END_PARAM_MSG_VAL]\n"

    # signal-attributes:
    out_str += "[START_PARAM_SIG_VAL]\n"
    for frame in db.frames:
        if frame.is_complex_multiplexed:
            continue

        for signal in frame.signals:
            for attrib, val in sorted(list(signal.attributes.items())):
                out_str += str(frame.arbitration_id.id) + ',S,' + signal.name + \
                    ',"' + attrib + '","' + val + '"\n'
    out_str += "[END_PARAM_SIG_VAL]\n"
    out_str += "[END_PARAM_VAL]\n"
    f.write(out_str.encode(dbf_export_encoding, ignore_encoding_errors))