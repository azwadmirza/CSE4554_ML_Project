    def func(self):
        """Perform the command"""
        account = self.account
        permstr = (
            account.is_superuser
            and " (superuser)"
            or "(%s)" % (", ".join(account.permissions.all()))
        )
        if self.cmdstring in ("unquell", "unquell"):
            if not account.attributes.get("_quell"):
                self.msg("Already using normal Account permissions %s." % permstr)
            else:
                account.attributes.remove("_quell")
                self.msg("Account permissions %s restored." % permstr)
        else:
            if account.attributes.get("_quell"):
                self.msg("Already quelling Account %s permissions." % permstr)
                return
            account.attributes.add("_quell", True)
            puppet = self.session.puppet if self.session else None
            if puppet:
                cpermstr = "(%s)" % ", ".join(puppet.permissions.all())
                cpermstr = "Quelling to current puppet's permissions %s." % cpermstr
                cpermstr += (
                    "\n(Note: If this is higher than Account permissions %s,"
                    " the lowest of the two will be used.)" % permstr
                )
                cpermstr += "\nUse unquell to return to normal permission usage."
                self.msg(cpermstr)
            else:
                self.msg("Quelling Account permissions%s. Use unquell to get them back." % permstr)
        self._recache_locks(account)