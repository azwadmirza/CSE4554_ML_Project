    def func(self):
        "Implement the function"

        switches = self.switches
        lhslist = self.lhslist

        if not self.args:
            self.msg("Usage: @sethelp/[add|del|append|merge] <topic>[,category[,locks,..] = <text>")
            return

        topicstr = ""
        category = "General"
        lockstring = "view:all()"
        try:
            topicstr = lhslist[0]
            category = lhslist[1]
            lockstring = ",".join(lhslist[2:])
        except Exception:
            pass

        if not topicstr:
            self.msg("You have to define a topic!")
            return
        # check if we have an old entry with the same name
        try:
            old_entry = HelpEntry.objects.get(db_key__iexact=topicstr)
        except Exception:
            old_entry = None

        if 'append' in switches or "merge" in switches:
            # merge/append operations
            if not old_entry:
                self.msg("Could not find topic '%s'. You must give an exact name." % topicstr)
                return
            if not self.rhs:
                self.msg("You must supply text to append/merge.")
                return
            if 'merge' in switches:
                old_entry.entrytext += " " + self.rhs
            else:
                old_entry.entrytext += "\n%s" % self.rhs
            self.msg("Entry updated:\n%s" % old_entry.entrytext)
            return
        if 'delete' in switches or 'del' in switches:
            # delete the help entry
            if not old_entry:
                self.msg("Could not find topic '%s'" % topicstr)
                return
            old_entry.delete()
            self.msg("Deleted help entry '%s'." % topicstr)
            return

        # at this point it means we want to add a new help entry.
        if not self.rhs:
            self.msg("You must supply a help text to add.")
            return
        if old_entry:
            if 'for' in switches or 'force' in switches:
                # overwrite old entry
                old_entry.key = topicstr
                old_entry.entrytext = self.rhs
                old_entry.help_category = category
                old_entry.locks.clear()
                old_entry.locks.add(lockstring)
                old_entry.save()
                self.msg("Overwrote the old topic '%s' with a new one." % topicstr)
            else:
                self.msg("Topic '%s' already exists. Use /force to overwrite or /append or /merge to add text to it." % topicstr)
        else:
            # no old entry. Create a new one.
            new_entry = create.create_help_entry(topicstr,
                                                 self.rhs, category, lockstring)
            if new_entry:
                self.msg("Topic '%s' was successfully created." % topicstr)
            else:
                self.msg("Error when creating topic '%s'! Contact an admin." % topicstr)