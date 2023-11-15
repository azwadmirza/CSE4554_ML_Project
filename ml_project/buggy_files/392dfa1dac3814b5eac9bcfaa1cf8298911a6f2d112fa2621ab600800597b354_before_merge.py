def sendMessage(sender="", recv="", broadcast=None, subject="", body="", reply=False):
    if sender == "":
        return
    d = Dialog(dialog="dialog")
    d.set_background_title("Send a message")
    if recv == "":
        r, t = d.inputbox("Recipient address (Cancel to load from the Address Book or leave blank to broadcast)", 10, 60)
        if r != d.DIALOG_OK:
            global menutab
            menutab = 6
            return
        recv = t
    if broadcast == None and sender != recv:
        r, t = d.radiolist("How to send the message?",
            choices=[("1", "Send to one or more specific people", True),
                ("2", "Broadcast to everyone who is subscribed to your address", False)])
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
                    d.set_background_title("Recipient address error")
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
                    d.scrollbox(unicode(err), exit_label="Continue")
                else:
                    addr = addBMIfNotPresent(addr)
                    if version > 4 or version <= 1:
                        d.set_background_title("Recipient address error")
                        d.scrollbox(unicode("Could not understand version number " + version + "of address" + addr + "."),
                            exit_label="Continue")
                        continue
                    if stream > 1 or stream == 0:
                        d.set_background_title("Recipient address error")
                        d.scrollbox(unicode("Bitmessage currently only supports stream numbers of 1, unlike as requested for address " + addr + "."),
                            exit_label="Continue")
                        continue
                    if len(shared.connectedHostsList) == 0:
                        d.set_background_title("Not connected warning")
                        d.scrollbox(unicode("Because you are not currently connected to the network, "),
                            exit_label="Continue")
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
            d.set_background_title("Empty sender error")
            d.scrollbox(unicode("You must specify an address to send the message from."),
                exit_label="Continue")
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