def dump(db, f, **options):  # type: (canmatrix.CanMatrix, typing.IO, **typing.Any) -> None
    """
    export canmatrix-object as .sym file (compatible to PEAK-Systems)
    """
    sym_encoding = options.get('symExportEncoding', 'iso-8859-1')
    ignore_encoding_errors = options.get("ignoreExportEncodingErrors", "")

    enum_dict = {}
    for enum_name, enum_values in db.value_tables.items():
        enum_dict[enum_name] = "enum {}({})".format(enum_name, ', '.join('{}="{}"'.format(*items) for items in sorted(enum_values.items())))
    enums = "{ENUMS}\n"

    header = """\
FormatVersion=5.0 // Do not edit this line!
Title=\"{}\"
""".format(db.attribute("Title", "canmatrix-Export"))
    f.write(header.encode(sym_encoding, ignore_encoding_errors))

    def send_receive(for_frame):
        return (
            for_frame.attributes.get('Sendable', 'True') == 'True',
            for_frame.attributes.get('Receivable', 'True') == 'True',
        )

    sections = collections.OrderedDict((
        ('SEND', tuple(f for f in db.frames if send_receive(f) == (True, False))),
        ('RECEIVE', tuple(f for f in db.frames if send_receive(f) == (False, True))),
        ('SENDRECEIVE', tuple(f for f in db.frames if send_receive(f) == (True, True))),
    ))

    output = '\n'

    for name, frames in sections.items():
        if len(frames) == 0:
            continue

        # Frames
        output += "{{{}}}\n\n".format(name)

        # trigger all frames
        for frame in frames:
            name = "[" + frame.name + "]\n"

            if frame.arbitration_id.extended == 1:
                id_type = "ID=%08Xh" % frame.arbitration_id.id
            else:
                id_type = "ID=%03Xh" % frame.arbitration_id.id
            if frame.comment is not None and len(frame.comment) > 0:
                id_type += "\t// " + \
                    frame.comment.replace('\n', ' ').replace('\r', ' ')
            id_type += "\n"
            if frame.arbitration_id.extended == 1:
                id_type += "Type=Extended\n"
            else:
                id_type += "Type=Standard\n"

            # check if frame has multiplexed signals
            multiplex = 0
            for signal in frame.signals:
                if signal.multiplex is not None:
                    multiplex = 1

            if multiplex == 1:
                # search for multiplexor in frame:
                for signal in frame.signals:
                    if signal.multiplex == 'Multiplexor':
                        mux_signal = signal

                # ticker all possible mux-groups as i (0 - 2^ (number of bits of multiplexor))
                first = 0
                for i in range(0, 1 << int(mux_signal.size)):
                    found = 0
                    mux_out = ""
                    # ticker all signals
                    for signal in frame.signals:
                        # if signal is in mux-group i
                        if signal.multiplex == i:
                            mux_out = name
                            if first == 0:
                                mux_out += id_type
                                first = 1
                            mux_out += "DLC=%d\n" % frame.size
                            if frame.cycle_time != 0:
                                mux_out += "CycleTime=" + str(frame.effective_cycle_time) + "\n"

                            mux_name = frame.mux_names.get(i, mux_signal.name + "%d" % i)

                            mux_out += "Mux=" + mux_name
                            start_bit = mux_signal.get_startbit()
                            s = str(i)
                            if len(s) > 1:
                                length = len(
                                    '{:X}'.format(int(mux_signal.calc_max()))
                                )
                                s = '{:0{}X}h'.format(i, length)
                            if not signal.is_little_endian:
                                # Motorola
                                mux_out += " %d,%d %s -m" % (start_bit, mux_signal.size, s)
                            else:
                                mux_out += " %d,%d %s" % (start_bit, mux_signal.size, s)
                            if not mux_out.endswith('h'):
                                mux_out += ' '
                            if i in mux_signal.comments:
                                comment = mux_signal.comments.get(i)
                                if len(comment) > 0:
                                    mux_out += '\t// ' + comment
                            mux_out += "\n"
                            found = 1
                            break

                    if found == 1:
                        for signal in frame.signals:
                            if signal.multiplex == i or signal.multiplex is None:
                                mux_out += create_signal(db, signal)
                                enum_dict.update(create_enum_from_signal_values(signal))
                        output += mux_out + "\n"

            else:
                # no multiplex signals in frame, just 'normal' signals
                output += name
                output += id_type
                output += "DLC=%d\n" % frame.size
                if frame.cycle_time != 0:
                    output += "CycleTime=" + str(frame.effective_cycle_time) + "\n"
                for signal in frame.signals:
                    output += create_signal(db, signal)
                    enum_dict.update(create_enum_from_signal_values(signal))
                output += "\n"
    enums += '\n'.join(sorted(enum_dict.values()))
    # write output file
    f.write((enums + '\n').encode(sym_encoding, ignore_encoding_errors))
    f.write(output.encode(sym_encoding, ignore_encoding_errors))