    def _post_connect(self):
        """! @brief Finish the connect process.
        
        The session is opened. The `no_init` parameter passed to the constructor determines whether the
        board and target are initialized.
        
        If an ELF file was provided on the command line, it is set on the target.
        
        @param self This object.
        @param session A @ref pyocd.core.session.Session "Session" instance.
        @retval True Session attached and context state inited successfully.
        @retval False An error occurred when opening the session or initing the context state.
        """
        assert self.session is not None
        assert not self.session.is_open
        
        # Open the session.
        try:
            self.session.open(init_board=not self.args.no_init)
        except exceptions.TransferFaultError as e:
            if not self.session.target.is_locked():
                self.context.writei("Transfer fault while initing board: %s", e)
                if self.session.log_tracebacks:
                    self.context.write(traceback.format_exc())
                return False
        except exceptions.Error as e:
            self.context.writei("Exception while initing board: %s", e)
            if self.session.log_tracebacks:
                self.context.write(traceback.format_exc())
            return False

        # Set elf file if provided.
        if self.args.elf:
            self.session.target.elf = os.path.expanduser(self.args.elf)

        # Handle a device with flash security enabled.
        if not self.args.no_init and self.session.target.is_locked():
            self.context.write("Warning: Target is locked, limited operations available. Use 'unlock' "
                                "command to mass erase and unlock, then execute 'reinit'.")
        
        return True