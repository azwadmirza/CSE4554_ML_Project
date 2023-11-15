def sendMessage(sender="", recv="", broadcast=None, subject="", body="", reply=False):
    if sender == "":
        return
    d = Dialog(dialog="dialog")
    set_background_title(d, "Send a message")
    if recv == "":
        r, t = d.inputbox("Recipient address (Cancel to load from the Address Book or leave blank to broadcast)", 10, 60)
        if r != d.DIALOG_OK:
            global menutab
            menutab = 6
            return
        recv = t
    if broadcast == None and sender != recv:
        r, t = d.radiolist("How to send the message?",
            choices=[("1", "Send to one or more specific people", 1),
                ("2", "Broadcast to everyone who is subscribed to your address", 0)])
        if r != d.DIALOG_OK:
            return
        broadcast = False
        if t == "2": # Broadcast
            broadcast = True
    if subject == "" or reply:
        r, t = d.inputbox("Message subject", width=60, init=subject)
        if r != d.DIALOG_OK:
            return
        subject = t
    if body == "" or reply:
        r, t = d.inputbox("Message body", 10, 80, init=body)
        if r != d.DIALOG_OK:
            return
        body = t
        body = body.replace("\\n", "\n").replace("\\t", "\t")

    if not broadcast:
        recvlist = []
        for i, item in enumerate(recv.replace(",", ";").split(";")):
            recvlist.append(item.strip())
        list(set(recvlist)) # Remove exact duplicates
        for addr in recvlist:
            if addr != "":
                status, version, stream, ripe = decodeAddress(addr)
                if status != "success":
                    set_background_title(d, "Recipient address error")
                    err = "Could not decode" + addr + " : " + status + "\n\n"
                    if status == "missingbm":
                        err += "Bitmessage addresses should start with \"BM-\"."
                    elif status == "checksumfailed":
                        err += "The address was not typed or copied correctly."
                    elif status == "invalidcharacters":
                        err += "The address contains invalid characters."
                    elif status == "versiontoohigh":
                        err += "The address version is too high. Either you need to upgrade your Bitmessage software or your acquaintance is doing something clever."
                    elif status == "ripetooshort":
                        err += "Some data encoded in the address is too short. There might be something wrong with the software of your acquaintance."
                    elif status == "ripetoolong":
                        err += "Some data encoded in the address is too long. There might be something wrong with the software of your acquaintance."
                    elif status == "varintmalformed":
                        err += "Some data encoded in the address is malformed. There might be something wrong with the software of your acquaintance."
                    else:
                        err += "It is unknown what is wrong with the address."
                    scrollbox(d, unicode(err))
                else:
                    addr = addBMIfNotPresent(addr)
                    if version > 4 or version <= 1:
                        set_background_title(d, "Recipient address error")
                        scrollbox(d, unicode("Could not understand version number " + version + "of address" + addr + "."))
                        continue
                    if stream > 1 or stream == 0:
                        set_background_title(d, "Recipient address error")
                        scrollbox(d, unicode("Bitmessage currently only supports stream numbers of 1, unlike as requested for address " + addr + "."))
                        continue
                    if len(shared.connectedHostsList) == 0:
                        set_background_title(d, "Not connected warning")
                        scrollbox(d, unicode("Because you are not currently connected to the network, "))
                    ackdata = OpenSSL.rand(32)
                    sqlExecute(
                        "INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        "",
                        addr,
                        ripe,
                        sender,
                        subject,
                        body,
                        ackdata,
                        int(time.time()), # sentTime (this will never change)
                        int(time.time()), # lastActionTime
                        0, # sleepTill time. This will get set when the POW gets done.
                        "msgqueued",
                        0, # retryNumber
                        "sent",
                        2, # encodingType
                        shared.config.getint('bitmessagesettings', 'ttl'))
                    shared.workerQueue.put(("sendmessage", addr))
    else: # Broadcast
        if recv == "":
            set_background_title(d, "Empty sender error")
            scrollbox(d, unicode("You must specify an address to send the message from."))
        else:
            ackdata = OpenSSL.rand(32)
            recv = BROADCAST_STR
            ripe = ""
            sqlExecute(
                "INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                "",
                recv,
                ripe,
                sender,
                subject,
                body,
                ackdata,
                int(time.time()), # sentTime (this will never change)
                int(time.time()), # lastActionTime
                0, # sleepTill time. This will get set when the POW gets done.
                "broadcastqueued",
                0, # retryNumber
                "sent", # folder
                2, # encodingType
                shared.config.getint('bitmessagesettings', 'ttl'))
            shared.workerQueue.put(('sendbroadcast', ''))