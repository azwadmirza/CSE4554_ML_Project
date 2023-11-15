def load(filename, **options):
    from sys import modules

    # use xlrd excel reader if available, because its more robust
    if 'xlsxLegacy' in options and options['xlsxLegacy'] == True:
        logger.error("xlsx: using legacy xlsx-reader - please get xlrd working for better results!")
    else:
        import canmatrix.xls
        return canmatrix.xls.load(filename, **options)

    # else use this hack to read xlsx
    if 'xlsMotorolaBitFormat' in options:
        motorolaBitFormat = options["xlsMotorolaBitFormat"]
    else:
        motorolaBitFormat = "msbreverse"

    sheet = readXlsx(filename, sheet=1, header=True)
    db = CanMatrix()
    letterIndex = []
    for a in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        letterIndex.append(a)
    for a in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        for b in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            letterIndex.append("%s%s" % (a, b))

    # Defines not imported...
    db.addFrameDefines("GenMsgCycleTime", 'INT 0 65535')
    db.addFrameDefines("GenMsgDelayTime", 'INT 0 65535')
    db.addFrameDefines("GenMsgCycleTimeActive", 'INT 0 65535')
    db.addFrameDefines("GenMsgNrOfRepetitions", 'INT 0 65535')
    launchTypes = []

    db.addSignalDefines("GenSigSNA", 'STRING')

    if 'Byteorder' in list(sheet[0].values()):
        for key in sheet[0]:
            if sheet[0][key].strip() == 'Byteorder':
                _BUstart = letterIndex.index(key) + 1
                break
    else:
        for key in sheet[0]:
            if sheet[0][key].strip() == 'Signal Not Available':
                _BUstart = letterIndex.index(key) + 1

    for key in sheet[0]:
        if sheet[0][key].strip() == 'Value':
            _BUend = letterIndex.index(key)

    # BoardUnits:
    for x in range(_BUstart, _BUend):
        db.addEcu(BoardUnit(sheet[0][letterIndex[x]]))

    # initialize:
    frameId = None
    signalName = ""
    newBo = None

    for row in sheet[1]:
        # ignore empty row
        if not 'ID' in row:
            continue
        # new frame detected
        if row['ID'] != frameId:
            sender = []
            # new Frame
            frameId = row['ID']
            frameName = row['Frame Name']
            cycleTime = getIfPossible(row, "Cycle Time [ms]")
            launchType = getIfPossible(row, 'Launch Type')
            dlc = 8
            launchParam = getIfPossible(row, 'Launch Parameter')
            if type(launchParam).__name__ != "float":
                launchParam = 0.0
            launchParam = str(int(launchParam))

            if frameId.endswith("xh"):
                newBo = Frame(frameName, id=int(frameId[:-2], 16), size=dlc, extended=True)
            else:
                newBo = Frame(frameName, id=int(frameId[:-1], 16), size=dlc)

            db.addFrame(newBo)

            # eval launchtype
            if launchType is not None:
                newBo.addAttribute("GenMsgSendType", launchType)
                if launchType not in launchTypes:
                    launchTypes.append(launchType)

#                       #eval cycletime
            if type(cycleTime).__name__ != "float":
                cycleTime = 0.0
            newBo.addAttribute("GenMsgCycleTime", str(int(cycleTime)))

        # new signal detected
        if 'Signal Name' in row and row['Signal Name'] != signalName:
            # new Signal
            receiver = []
            startbyte = int(row["Signal Byte No."])
            startbit = int(row['Signal Bit No.'])
            signalName = row['Signal Name']
            signalComment = getIfPossible(row, 'Signal Function')
            signalLength = int(row['Signal Length [Bit]'])
            signalDefault = getIfPossible(row, 'Signal Default')
            signalSNA = getIfPossible(row, 'Signal Not Available')
            multiplex = None
            if signalComment is not None and signalComment.startswith(
                    'Mode Signal:'):
                multiplex = 'Multiplexor'
                signalComment = signalComment[12:]
            elif signalComment is not None and signalComment.startswith('Mode '):
                mux, signalComment = signalComment[4:].split(':', 1)
                multiplex = int(mux.strip())

            signalByteorder = getIfPossible(row, 'Byteorder')
            if signalByteorder is not None:
                if 'i' in signalByteorder:
                    is_little_endian = True
                else:
                    is_little_endian = False
            else:
                is_little_endian = True  # Default Intel

            is_signed = False

            if signalName != "-":
                for x in range(_BUstart, _BUend):
                    buName = sheet[0][letterIndex[x]].strip()
                    buSenderReceiver = getIfPossible(row, buName)
                    if buSenderReceiver is not None:
                        if 's' in buSenderReceiver:
                            newBo.addTransmitter(buName)
                        if 'r' in buSenderReceiver:
                            receiver.append(buName)
#                if signalLength > 8:
#                    newSig = Signal(signalName, (startbyte-1)*8+startbit, signalLength, is_little_endian, is_signed, 1, 0, 0, 1, "", receiver, multiplex)
                newSig = Signal(signalName,
                                startBit=(startbyte - 1) * 8 + startbit,
                                size=signalLength,
                                is_little_endian=is_little_endian,
                                is_signed=is_signed,
                                receiver=receiver,
                                multiplex=multiplex)

#                else:
#                    newSig = Signal(signalName, (startbyte-1)*8+startbit, signalLength, is_little_endian, is_signed, 1, 0, 0, 1, "", receiver, multiplex)
                if is_little_endian == False:
                    # motorola
                    if motorolaBitFormat == "msb":
                        newSig.setStartbit(
                            (startbyte - 1) * 8 + startbit, bitNumbering=1)
                    elif motorolaBitFormat == "msbreverse":
                        newSig.setStartbit((startbyte - 1) * 8 + startbit)
                    else:  # motorolaBitFormat == "lsb"
                        newSig.setStartbit(
                            (startbyte - 1) * 8 + startbit,
                            bitNumbering=1,
                            startLittle=True)

                newBo.addSignal(newSig)
                newSig.addComment(signalComment)
                function = getIfPossible(row, 'Function / Increment Unit')
        value = getIfPossible(row, 'Value')
        valueName = getIfPossible(row, 'Name / Phys. Range')

        if valueName == 0 or valueName is None:
            valueName = "0"
        elif valueName == 1:
            valueName = "1"
        test = valueName
        #.encode('utf-8')

        factor = 0
        unit = ""

        factor = getIfPossible(row, 'Function / Increment Unit')
        if type(factor).__name__ == "unicode" or type(
                factor).__name__ == "str":
            factor = factor.strip()
            if " " in factor and factor[0].isdigit():
                (factor, unit) = factor.strip().split(" ", 1)
                factor = factor.strip()
                unit = unit.strip()
                newSig.unit = unit
                newSig.factor = float(factor)
            else:
                unit = factor.strip()
                newSig.unit = unit
                newSig.factor = 1

        if ".." in test:
            (mini, maxi) = test.strip().split("..", 2)
            unit = ""
            try:
                newSig.offset = float(mini)
                newSig.min = float(mini)
                newSig.max = float(maxi)
            except:
                newSig.offset = 0
                newSig.min = None
                newSig.max = None

        elif valueName.__len__() > 0:
            if value is not None and value.strip().__len__() > 0:
                value = int(float(value))
                newSig.addValues(value, valueName)
            maxi = pow(2, signalLength) - 1
            newSig.max = float(maxi)
        else:
            newSig.offset = 0
            newSig.min = None
            newSig.max = None

    # dlc-estimation / dlc is not in xls, thus calculate a minimum-dlc:
    for frame in db.frames:
        frame.updateReceiver()
        frame.calcDLC()

    launchTypeEnum = "ENUM"
    for launchType in launchTypes:
        if len(launchType) > 0:
            launchTypeEnum += ' "' + launchType + '",'
    db.addFrameDefines("GenMsgSendType", launchTypeEnum[:-1])

    db.setFdType()
    return db