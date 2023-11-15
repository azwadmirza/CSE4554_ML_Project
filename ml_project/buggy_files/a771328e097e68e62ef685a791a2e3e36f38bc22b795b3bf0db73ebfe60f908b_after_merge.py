    def func(self):
        """
        Implement all menu commands.
        """
        def _restore(caller):
            # check if there is a saved menu available.
            # this will re-start a completely new evmenu call.
            saved_options = caller.attributes.get("_menutree_saved")
            if saved_options:
                startnode = caller.attributes.get("_menutree_saved_startnode")
                if startnode:
                    saved_options[1]["startnode"] = startnode
                # this will create a completely new menu call
                EvMenu(caller, *saved_options[0], **saved_options[1])
                return True

        caller = self.caller
        menu = caller.ndb._menutree
        if not menu:
            if _restore(caller):
                return
            orig_caller = caller
            caller = caller.player if hasattr(caller, "player") else None
            menu = caller.ndb._menutree if caller else None
            if not menu:
                if caller and _restore(caller):
                    return
                caller = self.session
                menu = caller.ndb._menutree
                if not menu:
                    # can't restore from a session
                    err = "Menu object not found as %s.ndb._menutree!" % (orig_caller)
                    orig_caller.msg(err)
                    raise EvMenuError(err)

        # we have a menu, use it.
        menu._input_parser(menu, self.raw_string, caller)