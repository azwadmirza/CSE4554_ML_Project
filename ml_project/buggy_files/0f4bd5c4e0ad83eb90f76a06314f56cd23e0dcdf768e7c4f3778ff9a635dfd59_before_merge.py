    def func(self):
        subject = ""
        body = ""

        if self.switches or self.args:
            if "delete" in self.switches:
                try:
                    if not self.lhs:
                        self.caller.msg("No Message ID given.  Unable to delete.")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        mind = int(self.lhs) - 1
                        if all_mail[mind]:
                            all_mail[mind].delete()
                            self.caller.msg("Message %s deleted" % self.lhs)
                        else:
                            raise IndexError
                except IndexError:
                    self.caller.msg("That message does not exist.")
                except ValueError:
                    self.caller.msg("Usage: @mail/delete <message ID>")
            elif "forward" in self.switches:
                try:
                    if not self.rhs:
                        self.caller.msg("Cannot forward a message without an account list.  Please try again.")
                        return
                    elif not self.lhs:
                        self.caller.msg("You must define a message to forward.")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        if "/" in self.rhs:
                            message_number, message = self.rhs.split("/")
                            mind = int(message_number) - 1

                            if all_mail[mind]:
                                old_message = all_mail[mind]

                                self.send_mail(self.search_targets(self.lhslist), "FWD: " + old_message.header,
                                               message + "\n---- Original Message ----\n" + old_message.message,
                                               self.caller)
                                self.caller.msg("Message forwarded.")
                            else:
                                raise IndexError
                        else:
                            mind = int(self.rhs) - 1
                            if all_mail[mind]:
                                old_message = all_mail[mind]
                                self.send_mail(self.search_targets(self.lhslist), "FWD: " + old_message.header,
                                               "\n---- Original Message ----\n" + old_message.message, self.caller)
                                self.caller.msg("Message forwarded.")
                                old_message.tags.remove("u", category="mail")
                                old_message.tags.add("f", category="mail")
                            else:
                                raise IndexError
                except IndexError:
                    self.caller.msg("Message does not exixt.")
                except ValueError:
                    self.caller.msg("Usage: @mail/forward <account list>=<#>[/<Message>]")
            elif "reply" in self.switches:
                try:
                    if not self.rhs:
                        self.caller.msg("You must define a message to reply to.")
                        return
                    elif not self.lhs:
                        self.caller.msg("You must supply a reply message")
                        return
                    else:
                        all_mail = self.get_all_mail()
                        mind = int(self.lhs) - 1
                        if all_mail[mind]:
                            old_message = all_mail[mind]
                            self.send_mail(old_message.senders, "RE: " + old_message.header,
                                           self.rhs + "\n---- Original Message ----\n" + old_message.message, self.caller)
                            old_message.tags.remove("u", category="mail")
                            old_message.tags.add("r", category="mail")
                            return
                        else:
                            raise IndexError
                except IndexError:
                    self.caller.msg("Message does not exist.")
                except ValueError:
                    self.caller.msg("Usage: @mail/reply <#>=<message>")
            else:
                # normal send
                if self.rhs:
                    if "/" in self.rhs:
                        subject, body = self.rhs.split("/", 1)
                    else:
                        body = self.rhs
                    self.send_mail(self.search_targets(self.lhslist), subject, body, self.caller)
                else:
                    try:
                        message = self.get_all_mail()[int(self.lhs) - 1]
                    except (ValueError, IndexError):
                        self.caller.msg("'%s' is not a valid mail id." % self.lhs)
                        return

                    messageForm = []
                    if message:
                        messageForm.append(_HEAD_CHAR * _WIDTH)
                        messageForm.append("|wFrom:|n %s" % (message.senders[0].key))
                        messageForm.append("|wSent:|n %s" % message.db_date_created.strftime("%m/%d/%Y %H:%M:%S"))
                        messageForm.append("|wSubject:|n %s" % message.header)
                        messageForm.append(_SUB_HEAD_CHAR * _WIDTH)
                        messageForm.append(message.message)
                        messageForm.append(_HEAD_CHAR * _WIDTH)
                    self.caller.msg("\n".join(messageForm))
                    message.tags.remove("u", category="mail")
                    message.tags.add("o", category="mail")

        else:
            messages = self.get_all_mail()

            if messages:
                table = evtable.EvTable("|wID:|n", "|wFrom:|n", "|wSubject:|n", "|wDate:|n", "|wSta:|n",
                                        table=None, border="header", header_line_char=_SUB_HEAD_CHAR, width=_WIDTH)
                index = 1
                for message in messages:
                    table.add_row(index, message.senders[0], message.header,
                                  message.db_date_created.strftime("%m/%d/%Y"),
                                  str(message.db_tags.last().db_key.upper()))
                    index += 1

                table.reformat_column(0, width=6)
                table.reformat_column(1, width=17)
                table.reformat_column(2, width=34)
                table.reformat_column(3, width=13)
                table.reformat_column(4, width=7)

                self.caller.msg(_HEAD_CHAR * _WIDTH)
                self.caller.msg(unicode(table))
                self.caller.msg(_HEAD_CHAR * _WIDTH)
            else:
                self.caller.msg("There are no messages in your inbox.")