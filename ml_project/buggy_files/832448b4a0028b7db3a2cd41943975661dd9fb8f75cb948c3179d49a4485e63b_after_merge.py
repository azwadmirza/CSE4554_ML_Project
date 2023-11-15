def getSignals(signalarray, Bo, arDict, ns, multiplexId):
    GroupId = 1
    if signalarray is None:  # Empty signalarray - nothing to do
        return
    for signal in signalarray:
        values = {}
        motorolla = arGetChild(signal, "PACKING-BYTE-ORDER", arDict, ns)
        startBit = arGetChild(signal, "START-POSITION", arDict, ns)
        isignal = arGetChild(signal, "SIGNAL", arDict, ns)
        if isignal is None:
            isignal = arGetChild(signal, "I-SIGNAL", arDict, ns)
        if isignal is None:
            isignal = arGetChild(signal, "I-SIGNAL-GROUP", arDict, ns)
            if isignal is not None:
                logger.debug("getSignals: found I-SIGNAL-GROUP ")

                isignalarray = arGetXchildren(isignal, "I-SIGNAL", arDict, ns)
                getSysSignals(isignal, isignalarray, Bo, GroupId, ns)
                GroupId = GroupId + 1
                continue
        if isignal is None:
            logger.debug(
                'Frame %s, no isignal for %s found',
                Bo.name,
                arGetChild(
                    signal,
                    "SHORT-NAME",
                    arDict,
                    ns).text)
        syssignal = arGetChild(isignal, "SYSTEM-SIGNAL", arDict, ns)
        if syssignal is None:
            logger.debug(
                'Frame %s, signal %s has no systemsignal',
                isignal.tag,
                Bo.name)

        if "SYSTEM-SIGNAL-GROUP" in syssignal.tag:
            syssignalarray = arGetXchildren(
                syssignal, "SYSTEM-SIGNAL-REFS/SYSTEM-SIGNAL", arDict, ns)
            getSysSignals(syssignal, syssignalarray, Bo, GroupId, ns)
            GroupId = GroupId + 1
            continue

        length = arGetChild(isignal, "LENGTH", arDict, ns)
        if length is None:
            length = arGetChild(syssignal, "LENGTH", arDict, ns)
        name = arGetChild(syssignal, "SHORT-NAME", arDict, ns)

        unitElement = arGetChild(isignal, "UNIT", arDict, ns)
        displayName = arGetChild(unitElement, "DISPLAY-NAME", arDict, ns)
        if displayName is not None:
            Unit = displayName.text
        else:
            Unit = ""

        Min = None
        Max = None
        factor = 1.0
        offset = 0
        receiver = []

        signalDescription = getDesc(syssignal, arDict, ns)
        datatype = arGetChild(syssignal, "DATA-TYPE", arDict, ns)
        if datatype is None:  # AR4?
            dataConstr = arGetChild(isignal,"DATA-CONSTR", arDict, ns)
            compuMethod = arGetChild(isignal,"COMPU-METHOD", arDict, ns)
            baseType  = arGetChild(isignal,"BASE-TYPE", arDict, ns)

            lower = arGetChild(dataConstr, "LOWER-LIMIT", arDict, ns)
            upper = arGetChild(dataConstr, "UPPER-LIMIT", arDict, ns)
#            if lower is None: # data-constr has no limits defined - use limit from compu-method
#                lower = arGetChild(compuMethod, "LOWER-LIMIT", arDict, ns)
#            if upper is None: # data-constr has no limits defined - use limit from compu-method
#                upper = arGetChild(compuMethod, "UPPER-LIMIT", arDict, ns)
            encoding = None # TODO - find encoding in AR4
        else:
            lower = arGetChild(datatype, "LOWER-LIMIT", arDict, ns)
            upper = arGetChild(datatype, "UPPER-LIMIT", arDict, ns)
            encoding = arGetChild(datatype, "ENCODING", arDict, ns)

        if encoding is not None and (encoding.text == "SINGLE" or encoding.text == "DOUBLE"):
            is_float = True
        else:
            is_float = False
        
        if lower is not None and upper is not None:
            Min = float(lower.text)
            Max = float(upper.text)

        datdefprops = arGetChild(datatype, "SW-DATA-DEF-PROPS", arDict, ns)

        compmethod = arGetChild(datdefprops, "COMPU-METHOD", arDict, ns)
        if compmethod is None:  # AR4
            compmethod = arGetChild(isignal, "COMPU-METHOD", arDict, ns)
            baseType = arGetChild(isignal, "BASE-TYPE", arDict, ns)
            encoding = arGetChild(baseType, "BASE-TYPE-ENCODING", arDict, ns)
            if encoding is not None and encoding.text == "IEEE754":
                is_float = True
        #####################################################################################################
        # Modification to support sourcing the COMPU_METHOD info from the Vector NETWORK-REPRESENTATION-PROPS
        # keyword definition. 06Jun16
        #####################################################################################################
        if compmethod == None:
            logger.debug('No Compmethod found!! - try alternate scheme.')
            networkrep = arGetChild(isignal, "NETWORK-REPRESENTATION-PROPS", arDict, ns)
            datdefpropsvar = arGetChild(networkrep, "SW-DATA-DEF-PROPS-VARIANTS", arDict, ns)            
            datdefpropscond = arGetChild(datdefpropsvar, "SW-DATA-DEF-PROPS-CONDITIONAL", arDict ,ns)
            if datdefpropscond != None:
                try:
                    compmethod = arGetChild(datdefpropscond, "COMPU-METHOD", arDict, ns)            
                except:
                    logger.debug('No valid compu method found for this - check ARXML file!!')
                    compmethod = None
        #####################################################################################################
        #####################################################################################################
             
        unit = arGetChild(compmethod, "UNIT", arDict, ns)
        if unit is not None:
            longname = arGetChild(unit, "LONG-NAME", arDict, ns)
        #####################################################################################################
        # Modification to support obtaining the Signals Unit by DISPLAY-NAME. 07June16
        #####################################################################################################
            try:
              displayname = arGetChild(unit, "DISPLAY-NAME", arDict, ns)
            except:
              logger.debug('No Unit Display name found!! - using long name')
            if displayname is not None:
              Unit = displayname.text
            else:  
        #####################################################################################################
        #####################################################################################################              
              l4 = arGetChild(longname, "L-4", arDict, ns)
              if l4 is not None:
                Unit = l4.text

        compuscales = arGetXchildren(
            compmethod,
            "COMPU-INTERNAL-TO-PHYS/COMPU-SCALES/COMPU-SCALE",
            arDict,
            ns)

        initvalue = arGetXchildren(syssignal, "INIT-VALUE/VALUE", arDict, ns)

        if initvalue is None or initvalue.__len__() == 0:
            initvalue = arGetXchildren(isignal, "INIT-VALUE/NUMERICAL-VALUE-SPECIFICATION/VALUE", arDict, ns) ##AR4.2
        if initvalue is not None and initvalue.__len__() >= 1:
            initvalue = initvalue[0]
        else:
            initvalue = None

        for compuscale in compuscales:
            ll = arGetChild(compuscale, "LOWER-LIMIT", arDict, ns)
            ul = arGetChild(compuscale, "UPPER-LIMIT", arDict, ns)
            sl = arGetChild(compuscale, "SHORT-LABEL", arDict, ns)
            if sl is None:
                desc = getDesc(compuscale, arDict, ns)
            else:
                desc = sl.text
        #####################################################################################################
        # Modification to support sourcing the COMPU_METHOD info from the Vector NETWORK-REPRESENTATION-PROPS
        # keyword definition. 06Jun16
        #####################################################################################################
            if ll is not None and desc is not None and int(float(ul.text)) == int(float(ll.text)):
        #####################################################################################################
        #####################################################################################################
                values[ll.text] = desc

            scaleDesc = getDesc(compuscale, arDict, ns)
            rational = arGetChild(
                compuscale, "COMPU-RATIONAL-COEFFS", arDict, ns)
            if rational is not None:
                numerator = arGetChild(rational, "COMPU-NUMERATOR", arDict, ns)
                zaehler = arGetChildren(numerator, "V", arDict, ns)
                denominator = arGetChild(
                    rational, "COMPU-DENOMINATOR", arDict, ns)
                nenner = arGetChildren(denominator, "V", arDict, ns)

                factor = float(zaehler[1].text) / float(nenner[0].text)
                offset = float(zaehler[0].text) / float(nenner[0].text)
                if Min is not None:
                    Min *= factor
                    Min += offset
                if Max is not None:
                    Max *= factor
                    Max += offset
            else:
                const = arGetChild(compuscale, "COMPU-CONST", arDict, ns)
                # value hinzufuegen
                if const is None:
                    logger.warn(
                        "unknown Compu-Method: " +
                        compmethod.get('UUID'))
        is_little_endian = False
        if motorolla is not None:
            if motorolla.text == 'MOST-SIGNIFICANT-BYTE-LAST':
                is_little_endian = True
        else:
            logger.debug('no name byte order for signal' + name.text)

        is_signed = False  # unsigned
        if name is None:
            logger.debug('no name for signal given')
        if startBit is None:
            logger.debug('no startBit for signal given')
        if length is None:
            logger.debug('no length for signal given')

        if startBit is not None:
            newSig = Signal(name.text,
                            startBit=startBit.text,
                            signalSize=length.text,
                            is_little_endian=is_little_endian,
                            is_signed=is_signed,
                            factor=factor,
                            offset=offset,
                            min=Min,
                            max=Max,
                            unit=Unit,
                            receiver=receiver,
                            multiplex=multiplexId,
                            comment=signalDescription,
                            is_float=is_float)

            if newSig.is_little_endian == 0:
                # startbit of motorola coded signals are MSB in arxml
                newSig.setStartbit(int(startBit.text), bitNumbering=1)

            signalRxs[syssignal] = newSig

            basetype = arGetChild(datdefprops, "BASE-TYPE", arDict, ns)
            if basetype is not None:
                temp = arGetChild(basetype, "SHORT-NAME", arDict, ns)
                if temp is not None and "boolean" == temp.text:
                    newSig.addValues(1, "TRUE")
                    newSig.addValues(0, "FALSE")


            if initvalue is not None and initvalue.text is not None:
                if initvalue.text == "false":
                    initvalue.text = "0"
                elif initvalue.text == "true":
                    initvalue.text = "1"
                newSig._initValue = int(initvalue.text)
                newSig.addAttribute("GenSigStartValue", str(newSig._initValue))
            else:
                newSig._initValue = 0

            for key, value in list(values.items()):
                newSig.addValues(key, value)
            Bo.addSignal(newSig)