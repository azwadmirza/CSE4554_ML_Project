            def start():
                if self.combineRadio.GetValue():
                    self.progressDlg = wx.ProgressDialog(
                        "Creating new .torrents", "Please wait while Tribler is creating your .torrents.\n"
                        "This could take a while due to creating the required hashes.",
                        maximum=max, parent=self,
                        style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE)
                else:
                    self.progressDlg = wx.ProgressDialog(
                        "Creating new .torrents", "Please wait while Tribler is creating your .torrents.\n"
                        "This could take a while due to creating the required hashes.",
                        maximum=max, parent=self,
                        style=wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE)
                self.progressDlg.Pulse()
                self.progressDlg.cur = 0

                GUIUtility.getInstance().utility.session.lm.threadpool.call_in_thread(0, create_torrents)