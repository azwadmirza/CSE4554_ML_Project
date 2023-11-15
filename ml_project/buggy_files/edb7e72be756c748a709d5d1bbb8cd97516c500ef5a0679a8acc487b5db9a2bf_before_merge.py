    def _post_init(self):
        if GUIUtility.getInstance().utility.abcquitting:
            return

        some_ready = any([i.ready for i in self.boosting_manager.boosting_sources.values()])

        # if none are ready, keep waiting or If no source available
        if not some_ready and len(self.boosting_manager.boosting_sources.values()):
            self.guiutility.utility.session.lm.threadpool.add_task(self._post_init, 2,
                                                                   task_name=str(self) + "_post_init")
            return

        for _, source_obj in self.boosting_manager.boosting_sources.items():
            self.sourcelist.create_source_item(source_obj)

        self.sourcelist.Show()
        self.main_splitter.ReplaceWindow(self.loading_holder, self.sourcelist)
        self.loading_holder.Close()

        self.Bind(ULC.EVT_LIST_ITEM_SELECTED, self.on_sourceitem_selected, self.sourcelist)

        self.guiutility.utility.session.lm.threadpool.add_task(self.sourcelist.load_more, 2,
                                                               task_name=str(self) + "load_more")
        self.Layout()