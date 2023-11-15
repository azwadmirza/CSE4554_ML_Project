def handlech(c, stdscr):
    if c != curses.ERR:
        global inboxcur, addrcur, sentcur, subcur, abookcur, blackcur
        if c in range(256): 
            if chr(c) in '12345678':
                global menutab
                menutab = int(chr(c))
            elif chr(c) == 'q':
                global quit
                quit = True
            elif chr(c) == '\n':
                curses.curs_set(1)
                d = Dialog(dialog="dialog")
                if menutab == 1:
                    d.set_background_title("Inbox Message Dialog Box")
                    r, t = d.menu("Do what with \""+inbox[inboxcur][5]+"\" from \""+inbox[inboxcur][3]+"\"?",
                        choices=[("1", "View message"),
                            ("2", "Mark message as unread"),
                            ("3", "Reply"),
                            ("4", "Add sender to Address Book"),
                            ("5", "Save message as text file"),
                            ("6", "Move to trash")])
                    if r == d.DIALOG_OK:
                        if t == "1": # View
                            d.set_background_title("\""+inbox[inboxcur][5]+"\" from \""+inbox[inboxcur][3]+"\" to \""+inbox[inboxcur][1]+"\"")
                            data = ""
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                            if ret != []:
                                for row in ret:
                                    data, = row
                                data = shared.fixPotentiallyInvalidUTF8Data(data)
                                msg = ""
                                for i, item in enumerate(data.split("\n")):
                                    msg += fill(item, replace_whitespace=False)+"\n"
                                d.scrollbox(unicode(ascii(msg)), 30, 80, exit_label="Continue")
                                sqlExecute("UPDATE inbox SET read=1 WHERE msgid=?", inbox[inboxcur][0])
                                inbox[inboxcur][7] = 1
                            else:
                                d.scrollbox(unicode("Could not fetch message."), exit_label="Continue")
                        elif t == "2": # Mark unread
                            sqlExecute("UPDATE inbox SET read=0 WHERE msgid=?", inbox[inboxcur][0])
                            inbox[inboxcur][7] = 0
                        elif t == "3": # Reply
                            curses.curs_set(1)
                            m = inbox[inboxcur]
                            fromaddr = m[4]
                            ischan = False
                            for i, item in enumerate(addresses):
                                if fromaddr == item[2] and item[3] != 0:
                                    ischan = True
                                    break
                            if not addresses[i][1]:
                                d.scrollbox(unicode("Sending address disabled, please either enable it or choose a different address."), exit_label="Continue")
                                return
                            toaddr = m[2]
                            if ischan:
                                toaddr = fromaddr
                            
                            subject = m[5]
                            if not m[5][:4] == "Re: ":
                                subject = "Re: "+m[5]
                            body = ""
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", m[0])
                            if ret != []:
                                body = "\n\n------------------------------------------------------\n"
                                for row in ret:
                                    body, = row
                            
                            sendMessage(fromaddr, toaddr, ischan, subject, body, True)
                            dialogreset(stdscr)
                        elif t == "4": # Add to Address Book
                            global addrbook
                            addr = inbox[inboxcur][4]
                            if addr not in [item[1] for i,item in enumerate(addrbook)]:
                                r, t = d.inputbox("Label for address \""+addr+"\"")
                                if r == d.DIALOG_OK:
                                    label = t
                                    sqlExecute("INSERT INTO addressbook VALUES (?,?)", label, addr)
                                    # Prepend entry
                                    addrbook.reverse()
                                    addrbook.append([label, addr])
                                    addrbook.reverse()
                            else:
                                d.scrollbox(unicode("The selected address is already in the Address Book."), exit_label="Continue")
                        elif t == "5": # Save message
                            d.set_background_title("Save \""+inbox[inboxcur][5]+"\" as text file")
                            r, t = d.inputbox("Filename", init=inbox[inboxcur][5]+".txt")
                            if r == d.DIALOG_OK:
                                msg = ""
                                ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                                if ret != []:
                                    for row in ret:
                                        msg, = row
                                    fh = open(t, "a") # Open in append mode just in case
                                    fh.write(msg)
                                    fh.close()
                                else:
                                    d.scrollbox(unicode("Could not fetch message."), exit_label="Continue")
                        elif t == "6": # Move to trash
                            sqlExecute("UPDATE inbox SET folder='trash' WHERE msgid=?", inbox[inboxcur][0])
                            del inbox[inboxcur]
                            d.scrollbox(unicode("Message moved to trash. There is no interface to view your trash, \nbut the message is still on disk if you are desperate to recover it."),
                                exit_label="Continue")
                elif menutab == 2:
                    a = ""
                    if addresses[addrcur][3] != 0: # if current address is a chan
                        a = addresses[addrcur][2]
                    sendMessage(addresses[addrcur][2], a)
                elif menutab == 3:
                    d.set_background_title("Sent Messages Dialog Box")
                    r, t = d.menu("Do what with \""+sentbox[sentcur][4]+"\" to \""+sentbox[sentcur][0]+"\"?",
                        choices=[("1", "View message"),
                            ("2", "Move to trash")])
                    if r == d.DIALOG_OK:
                        if t == "1": # View
                            d.set_background_title("\""+sentbox[sentcur][4]+"\" from \""+sentbox[sentcur][3]+"\" to \""+sentbox[sentcur][1]+"\"")
                            data = ""
                            ret = sqlQuery("SELECT message FROM sent WHERE subject=? AND ackdata=?", sentbox[sentcur][4], sentbox[sentcur][6])
                            if ret != []:
                                for row in ret:
                                    data, = row
                                data = shared.fixPotentiallyInvalidUTF8Data(data)
                                msg = ""
                                for i, item in enumerate(data.split("\n")):
                                    msg += fill(item, replace_whitespace=False)+"\n"
                                d.scrollbox(unicode(ascii(msg)), 30, 80, exit_label="Continue")
                            else:
                                d.scrollbox(unicode("Could not fetch message."), exit_label="Continue")
                        elif t == "2": # Move to trash
                            sqlExecute("UPDATE sent SET folder='trash' WHERE subject=? AND ackdata=?", sentbox[sentcur][4], sentbox[sentcur][6])
                            del sentbox[sentcur]
                            d.scrollbox(unicode("Message moved to trash. There is no interface to view your trash, \nbut the message is still on disk if you are desperate to recover it."),
                                exit_label="Continue")
                elif menutab == 4:
                    d.set_background_title("Your Identities Dialog Box")
                    r, t = d.menu("Do what with \""+addresses[addrcur][0]+"\" : \""+addresses[addrcur][2]+"\"?",
                        choices=[("1", "Create new address"),
                            ("2", "Send a message from this address"),
                            ("3", "Rename"),
                            ("4", "Enable"),
                            ("5", "Disable"),
                            ("6", "Delete"),
                            ("7", "Special address behavior")])
                    if r == d.DIALOG_OK:
                        if t == "1": # Create new address
                            d.set_background_title("Create new address")
                            d.scrollbox(unicode("Here you may generate as many addresses as you like.\n"
                                "Indeed, creating and abandoning addresses is encouraged.\n"
                                "Deterministic addresses have several pros and cons:\n"
                                "\nPros:\n"
                                "  * You can recreate your addresses on any computer from memory\n"
                                "  * You need not worry about backing up your keys.dat file as long as you \n    can remember your passphrase\n"
                                "Cons:\n"
                                "  * You must remember (or write down) your passphrase in order to recreate \n    your keys if they are lost\n"
                                "  * You must also remember the address version and stream numbers\n"
                                "  * If you choose a weak passphrase someone may be able to brute-force it \n    and then send and receive messages as you"),
                                exit_label="Continue")
                            r, t = d.menu("Choose an address generation technique",
                                choices=[("1", "Use a random number generator"),
                                    ("2", "Use a passphrase")])
                            if r == d.DIALOG_OK:
                                if t == "1":
                                    d.set_background_title("Randomly generate address")
                                    r, t = d.inputbox("Label (not shown to anyone except you)")
                                    label = ""
                                    if r == d.DIALOG_OK and len(t) > 0:
                                        label = t
                                    r, t = d.menu("Choose a stream",
                                        choices=[("1", "Use the most available stream"),("", "(Best if this is the first of many addresses you will create)"),
                                            ("2", "Use the same stream as an existing address"),("", "(Saves you some bandwidth and processing power)")])
                                    if r == d.DIALOG_OK:
                                        if t == "1":
                                            stream = 1
                                        elif t == "2":
                                            addrs = []
                                            for i, item in enumerate(addresses):
                                                addrs.append([str(i), item[2]])
                                            r, t = d.menu("Choose an existing address's stream", choices=addrs)
                                            if r == d.DIALOG_OK:
                                                stream = decodeAddress(addrs[int(t)][1])[2]
                                        shorten = False
                                        r, t = d.checklist("Miscellaneous options",
                                            choices=[("1", "Spend time shortening the address", shorten)])
                                        if r == d.DIALOG_OK and "1" in t:
                                            shorten = True
                                        shared.addressGeneratorQueue.put(("createRandomAddress", 4, stream, label, 1, "", shorten))
                                elif t == "2":
                                    d.set_background_title("Make deterministic addresses")
                                    r, t = d.passwordform("Enter passphrase",
                                        [("Passphrase", 1, 1, "", 2, 1, 64, 128),
                                        ("Confirm passphrase", 3, 1, "", 4, 1, 64, 128)],
                                        form_height=4, insecure=True)
                                    if r == d.DIALOG_OK:
                                        if t[0] == t[1]:
                                            passphrase = t[0]
                                            r, t = d.rangebox("Number of addresses to generate",
                                                width=48, min=1, max=99, init=8)
                                            if r == d.DIALOG_OK:
                                                number = t
                                                stream = 1
                                                shorten = False
                                                r, t = d.checklist("Miscellaneous options",
                                                    choices=[("1", "Spend time shortening the address", shorten)])
                                                if r == d.DIALOG_OK and "1" in t:
                                                    shorten = True
                                                d.scrollbox(unicode("In addition to your passphrase, be sure to remember the following numbers:\n"
                                                    "\n  * Address version number: "+str(4)+"\n"
                                                    "  * Stream number: "+str(stream)),
                                                    exit_label="Continue")
                                                shared.addressGeneratorQueue.put(('createDeterministicAddresses', 4, stream, "unused deterministic address", number, str(passphrase), shorten))
                                        else:
                                            d.scrollbox(unicode("Passphrases do not match"), exit_label="Continue")
                        elif t == "2": # Send a message
                            a = ""
                            if addresses[addrcur][3] != 0: # if current address is a chan
                                a = addresses[addrcur][2]
                            sendMessage(addresses[addrcur][2], a)
                        elif t == "3": # Rename address label
                            a = addresses[addrcur][2]
                            label = addresses[addrcur][0]
                            r, t = d.inputbox("New address label", init=label)
                            if r == d.DIALOG_OK:
                                label = t
                                shared.config.set(a, "label", label)
                                # Write config
                                shared.writeKeysFile()
                                addresses[addrcur][0] = label
                        elif t == "4": # Enable address
                            a = addresses[addrcur][2]
                            shared.config.set(a, "enabled", "true") # Set config
                            # Write config
                            shared.writeKeysFile()
                            # Change color
                            if shared.safeConfigGetBoolean(a, 'chan'):
                                addresses[addrcur][3] = 9 # orange
                            elif shared.safeConfigGetBoolean(a, 'mailinglist'):
                                addresses[addrcur][3] = 5 # magenta
                            else:
                                addresses[addrcur][3] = 0 # black
                            addresses[addrcur][1] = True
                            shared.reloadMyAddressHashes() # Reload address hashes
                        elif t == "5": # Disable address
                            a = addresses[addrcur][2]
                            shared.config.set(a, "enabled", "false") # Set config
                            addresses[addrcur][3] = 8 # Set color to gray
                            # Write config
                            shared.writeKeysFile()
                            addresses[addrcur][1] = False
                            shared.reloadMyAddressHashes() # Reload address hashes
                        elif t == "6": # Delete address
                            r, t = d.inputbox("Type in \"I want to delete this address\"", width=50)
                            if r == d.DIALOG_OK and t == "I want to delete this address":
                                    shared.config.remove_section(addresses[addrcur][2])
                                    shared.writeKeysFile()
                                    del addresses[addrcur]
                        elif t == "7": # Special address behavior
                            a = addresses[addrcur][2]
                            d.set_background_title("Special address behavior")
                            if shared.safeConfigGetBoolean(a, "chan"):
                                d.scrollbox(unicode("This is a chan address. You cannot use it as a pseudo-mailing list."), exit_label="Continue")
                            else:
                                m = shared.safeConfigGetBoolean(a, "mailinglist")
                                r, t = d.radiolist("Select address behavior",
                                    choices=[("1", "Behave as a normal address", not m),
                                        ("2", "Behave as a pseudo-mailing-list address", m)])
                                if r == d.DIALOG_OK:
                                    if t == "1" and m == True:
                                        shared.config.set(a, "mailinglist", "false")
                                        if addresses[addrcur][1]:
                                            addresses[addrcur][3] = 0 # Set color to black
                                        else:
                                            addresses[addrcur][3] = 8 # Set color to gray
                                    elif t == "2" and m == False:
                                        try:
                                            mn = shared.config.get(a, "mailinglistname")
                                        except ConfigParser.NoOptionError:
                                           mn = ""
                                        r, t = d.inputbox("Mailing list name", init=mn)
                                        if r == d.DIALOG_OK:
                                            mn = t
                                            shared.config.set(a, "mailinglist", "true")
                                            shared.config.set(a, "mailinglistname", mn)
                                            addresses[addrcur][3] = 6 # Set color to magenta
                                    # Write config
                                    shared.writeKeysFile()
                elif menutab == 5:
                    d.set_background_title("Subscriptions Dialog Box")
                    r, t = d.menu("Do what with subscription to \""+subscriptions[subcur][0]+"\"?",
                        choices=[("1", "Add new subscription"),
                            ("2", "Delete this subscription"),
                            ("3", "Enable"),
                            ("4", "Disable")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            r, t = d.inputbox("New subscription address")
                            if r == d.DIALOG_OK:
                                addr = addBMIfNotPresent(t)
                                if not shared.isAddressInMySubscriptionsList(addr):
                                    r, t = d.inputbox("New subscription label")
                                    if r == d.DIALOG_OK:
                                        label = t
                                        # Prepend entry
                                        subscriptions.reverse()
                                        subscriptions.append([label, addr, True])
                                        subscriptions.reverse()

                                        sqlExecute("INSERT INTO subscriptions VALUES (?,?,?)", label, address, True)
                                        shared.reloadBroadcastSendersForWhichImWatching()
                        elif t == "2":
                            r, t = d.inpuxbox("Type in \"I want to delete this subscription\"")
                            if r == d.DIALOG_OK and t == "I want to delete this subscription":
                                    sqlExecute("DELETE FROM subscriptions WHERE label=? AND address=?", subscriptions[subcur][0], subscriptions[subcur][1])
                                    shared.reloadBroadcastSendersForWhichImWatching()
                                    del subscriptions[subcur]
                        elif t == "3":
                            sqlExecute("UPDATE subscriptions SET enabled=1 WHERE label=? AND address=?", subscriptions[subcur][0], subscriptions[subcur][1])
                            shared.reloadBroadcastSendersForWhichImWatching()
                            subscriptions[subcur][2] = True
                        elif t == "4":
                            sqlExecute("UPDATE subscriptions SET enabled=0 WHERE label=? AND address=?", subscriptions[subcur][0], subscriptions[subcur][1])
                            shared.reloadBroadcastSendersForWhichImWatching()
                            subscriptions[subcur][2] = False
                elif menutab == 6:
                    d.set_background_title("Address Book Dialog Box")
                    r, t = d.menu("Do what with \""+addrbook[abookcur][0]+"\" : \""+addrbook[abookcur][1]+"\"",
                        choices=[("1", "Send a message to this address"),
                            ("2", "Subscribe to this address"),
                            ("3", "Add new address to Address Book"),
                            ("4", "Delete this address")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            sendMessage(recv=addrbook[abookcur][1])
                        elif t == "2":
                            r, t = d.inputbox("New subscription label")
                            if r == d.DIALOG_OK:
                                label = t
                                # Prepend entry
                                subscriptions.reverse()
                                subscriptions.append([label, addr, True])
                                subscriptions.reverse()

                                sqlExecute("INSERT INTO subscriptions VALUES (?,?,?)", label, address, True)
                                shared.reloadBroadcastSendersForWhichImWatching()
                        elif t == "3":
                            r, t = d.inputbox("Input new address")
                            if r == d.DIALOG_OK:
                                addr = t
                                if addr not in [item[1] for i,item in enumerate(addrbook)]:
                                    r, t = d.inputbox("Label for address \""+addr+"\"")
                                    if r == d.DIALOG_OK:
                                        sqlExecute("INSERT INTO addressbook VALUES (?,?)", t, addr)
                                        # Prepend entry
                                        addrbook.reverse()
                                        addrbook.append([t, addr])
                                        addrbook.reverse()
                                else:
                                    d.scrollbox(unicode("The selected address is already in the Address Book."), exit_label="Continue")
                        elif t == "4":
                            r, t = d.inputbox("Type in \"I want to delete this Address Book entry\"")
                            if r == d.DIALOG_OK and t == "I want to delete this Address Book entry":
                                sqlExecute("DELETE FROM addressbook WHERE label=? AND address=?", addrbook[abookcur][0], addrbook[abookcur][1])
                                del addrbook[abookcur]
                elif menutab == 7:
                    d.set_background_title("Blacklist Dialog Box")
                    r, t = d.menu("Do what with \""+blacklist[blackcur][0]+"\" : \""+blacklist[blackcur][1]+"\"?",
                        choices=[("1", "Delete"),
                            ("2", "Enable"),
                            ("3", "Disable")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            r, t = d.inputbox("Type in \"I want to delete this Blacklist entry\"")
                            if r == d.DIALOG_OK and t == "I want to delete this Blacklist entry":
                                sqlExecute("DELETE FROM blacklist WHERE label=? AND address=?", blacklist[blackcur][0], blacklist[blackcur][1])
                                del blacklist[blackcur]
                        elif t == "2":
                            sqlExecute("UPDATE blacklist SET enabled=1 WHERE label=? AND address=?", blacklist[blackcur][0], blacklist[blackcur][1])
                            blacklist[blackcur][2] = True
                        elif t== "3":
                            sqlExecute("UPDATE blacklist SET enabled=0 WHERE label=? AND address=?", blacklist[blackcur][0], blacklist[blackcur][1])
                            blacklist[blackcur][2] = False
                dialogreset(stdscr)
        else:
            if c == curses.KEY_UP:
                if menutab == 1 and inboxcur > 0:
                    inboxcur -= 1
                if (menutab == 2 or menutab == 4) and addrcur > 0:
                    addrcur -= 1
                if menutab == 3 and sentcur > 0:
                    sentcur -= 1
                if menutab == 5 and subcur > 0:
                    subcur -= 1
                if menutab == 6 and abookcur > 0:
                    abookcur -= 1
                if menutab == 7 and blackcur > 0:
                    blackcur -= 1
            elif c == curses.KEY_DOWN:
                if menutab == 1 and inboxcur < len(inbox)-1:
                    inboxcur += 1
                if (menutab == 2 or menutab == 4) and addrcur < len(addresses)-1:
                    addrcur += 1
                if menutab == 3 and sentcur < len(sentbox)-1:
                    sentcur += 1
                if menutab == 5 and subcur < len(subscriptions)-1:
                    subcur += 1
                if menutab == 6 and abookcur < len(addrbook)-1:
                    abookcur += 1
                if menutab == 7 and blackcur < len(blacklist)-1:
                    blackcur += 1
            elif c == curses.KEY_HOME:
                if menutab == 1:
                    inboxcur = 0
                if menutab == 2 or menutab == 4:
                    addrcur = 0
                if menutab == 3:
                    sentcur = 0
                if menutab == 5:
                    subcur = 0
                if menutab == 6:
                    abookcur = 0
                if menutab == 7:
                    blackcur = 0
            elif c == curses.KEY_END:
                if menutab == 1:
                    inboxcur = len(inbox)-1
                if menutab == 2 or menutab == 4:
                    addrcur = len(addresses)-1
                if menutab == 3:
                    sentcur = len(sentbox)-1
                if menutab == 5:
                    subcur = len(subscriptions)-1
                if menutab == 6:
                    abookcur = len(addrbook)-1
                if menutab == 7:
                    blackcur = len(blackcur)-1
        redraw(stdscr)