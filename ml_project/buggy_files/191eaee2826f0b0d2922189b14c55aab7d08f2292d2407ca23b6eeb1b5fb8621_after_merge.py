    def __create_s5(self, tree_root, sizer):
        exp_panel, exp_vsizer = create_section(self, sizer, "Experimental")

        item_id = self._tree_ctrl.AppendItem(tree_root, "Experimental", data=wx.TreeItemData(exp_panel))

        # Web UI
        exp_s1_sizer = create_subsection(exp_panel, exp_vsizer, "Web UI", 2, 3)
        self._use_webui = wx.CheckBox(exp_panel, label="Enable webUI")
        exp_s1_sizer.Add(self._use_webui, 0, wx.EXPAND)
        exp_s1_sizer.AddStretchSpacer()

        add_label(exp_panel, exp_s1_sizer, label="Current port")
        self._webui_port = EditText(exp_panel, validator=NumberValidator(min=1, max=65535))
        exp_s1_sizer.Add(self._webui_port, 0, wx.EXPAND)

        exp_s1_faq_text = wx.StaticText(
            exp_panel, label="The Tribler webUI implements the same API as uTorrent.\nThus all uTorrent remotes are compatible with it.\n\nFurthermore, we additionally allow you to control Tribler\nusing your Browser. Go to http://localhost:PORT/gui to\nview your downloads in the browser.")
        exp_vsizer.Add(exp_s1_faq_text, 0, wx.EXPAND | wx.TOP, 10)

        # Emercoin
        exp_s2_sizer = create_subsection(exp_panel, exp_vsizer, "Emercoin", 2, 3)
        self._use_emc = wx.CheckBox(exp_panel, label="Enable Emercoin integration")
        exp_s2_sizer.Add(self._use_emc, 0, wx.EXPAND)
        exp_s2_sizer.AddStretchSpacer()

        add_label(exp_panel, exp_s2_sizer, "Server")
        self._emc_ip = wx.TextCtrl(exp_panel, style=wx.TE_PROCESS_ENTER)
        exp_s2_sizer.Add(self._emc_ip, 0, wx.EXPAND)

        add_label(exp_panel, exp_s2_sizer, "Port")
        self._emc_port = EditText(exp_panel, validator=NumberValidator(min=1, max=65535))
        exp_s2_sizer.Add(self._emc_port, 0, wx.EXPAND)

        add_label(exp_panel, exp_s2_sizer, "Username")
        self._emc_username = wx.TextCtrl(exp_panel, style=wx.TE_PROCESS_ENTER)
        self._emc_username.SetMaxLength(255)
        exp_s2_sizer.Add(self._emc_username, 0, wx.EXPAND)

        add_label(exp_panel, exp_s2_sizer, "Password")
        self._emc_password = wx.TextCtrl(exp_panel, style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
        self._emc_password.SetMaxLength(255)
        exp_s2_sizer.Add(self._emc_password, 0, wx.EXPAND)

        exp_s2_faq_text = wx.StaticText(
            exp_panel, label="Tribler connects to Emercoin over its JSON-RPC API.\nThis requires you to enable it by editing the emercoin.conf file and setting\nserver=1, rpcport, rpcuser, rpcpassword, and rpcconnect.")
        exp_vsizer.Add(exp_s2_faq_text, 0, wx.EXPAND | wx.TOP, 10)

        # load values
        self._use_webui.SetValue(self.utility.read_config('use_webui'))
        self._webui_port.SetValue(str(self.utility.read_config('webui_port')))

        self._use_emc.SetValue(self.utility.read_config('use_emc'))
        self._emc_ip.SetValue(self.utility.read_config('emc_ip'))
        self._emc_port.SetValue(str(self.utility.read_config('emc_port')))
        self._emc_username.SetValue(self.utility.read_config('emc_username'))
        self._emc_password.SetValue(self.utility.read_config('emc_password'))

        return exp_panel, item_id