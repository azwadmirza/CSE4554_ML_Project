    def browseDir(self, event):
        """
        Show the DirDialog and ask the user to change the directory where machine labels are stored
        """
        self.statusbar.SetStatusText("Looking for a folder to start labeling...")
        cwd = os.path.join(os.getcwd(), "labeled-data")
        dlg = wx.DirDialog(
            self,
            "Choose the directory where your extracted frames are saved:",
            cwd,
            style=wx.DD_DEFAULT_STYLE,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self.dir = dlg.GetPath()
            self.load.Enable(False)
            self.next.Enable(True)
            self.save.Enable(True)
        else:
            dlg.Destroy()
            self.Close(True)
            return
        dlg.Destroy()

        # Enabling the zoom, pan and home buttons
        self.zoom.Enable(True)
        self.home.Enable(True)
        self.pan.Enable(True)
        self.lock.Enable(True)

        # Reading config file and its variables
        self.cfg = auxiliaryfunctions.read_config(self.config_file)
        self.scorer = self.cfg["scorer"]
        (
            individuals,
            uniquebodyparts,
            multianimalbodyparts,
        ) = auxfun_multianimal.extractindividualsandbodyparts(self.cfg)

        self.multibodyparts = multianimalbodyparts
        # checks for unique bodyparts
        if len(self.multibodyparts) != len(set(self.multibodyparts)):
            print(
                "Error - bodyparts must have unique labels! Please choose unique bodyparts in config.yaml file and try again. Quitting for now!"
            )
            self.Close(True)

        self.uniquebodyparts = uniquebodyparts
        self.individual_names = individuals

        self.videos = self.cfg["video_sets"].keys()
        self.markerSize = self.cfg["dotsize"]
        self.edgewidth = self.markerSize // 3
        self.alpha = self.cfg["alphavalue"]
        self.colormap = plt.get_cmap(self.cfg["colormap"])
        self.colormap = self.colormap.reversed()
        self.idmap = plt.cm.get_cmap("Set1", len(individuals))
        self.project_path = self.cfg["project_path"]

        if self.uniquebodyparts == []:
            self.are_unique_bodyparts_present = False

        self.buttonCounter = {i: [] for i in self.individual_names}
        self.index = np.sort(
            [
                fn
                for fn in glob.glob(os.path.join(self.dir, "*.png"))
                if ("labeled.png" not in fn)
            ]
        )
        self.statusbar.SetStatusText(
            "Working on folder: {}".format(os.path.split(str(self.dir))[-1])
        )
        self.relativeimagenames = [
            "labeled" + n.split("labeled")[1] for n in self.index
        ]  # [n.split(self.project_path+'/')[1] for n in self.index]

        # Reading the existing dataset,if already present
        try:
            self.dataFrame = pd.read_hdf(
                os.path.join(self.dir, "CollectedData_" + self.scorer + ".h5"),
                "df_with_missing",
            )
            # Handle data previously labeled on a different platform
            sep = "/" if "/" in self.dataFrame.index[0] else "\\"
            if sep != os.path.sep:
                self.dataFrame.index = self.dataFrame.index.str.replace(
                    sep, os.path.sep
                )
            self.dataFrame.sort_index(inplace=True)
            self.prev.Enable(True)
            # Finds the first empty row in the dataframe and sets the iteration to that index
            self.iter = np.argmax(np.isnan(self.dataFrame.values).all(axis=1))
        except FileNotFoundError:
            # Create an empty data frame
            self.dataFrame = MainFrame.create_dataframe(
                self,
                self.dataFrame,
                self.relativeimagenames,
                self.individual_names,
                self.uniquebodyparts,
                self.multibodyparts,
            )
            self.iter = 0

        # Cache original bodyparts
        self._old_multi = (
            self.dataFrame.xs(self.individual_names[0], axis=1, level="individuals")
            .columns.get_level_values("bodyparts")
            .unique()
            .to_list()
        )
        self._old_unique = (
            self.dataFrame.loc[
                :, self.dataFrame.columns.get_level_values("individuals") == "single"
            ]
            .columns.get_level_values("bodyparts")
            .unique()
            .to_list()
        )

        # Reading the image name
        self.img = self.index[self.iter]
        img_name = Path(self.index[self.iter]).name

        # Checking for new frames and adding them to the existing dataframe
        old_imgs = np.sort(list(self.dataFrame.index))
        self.newimages = list(set(self.relativeimagenames) - set(old_imgs))
        if self.newimages:
            print("Found new frames..")
            # Create an empty dataframe with all the new images and then merge this to the existing dataframe.
            self.df = MainFrame.create_dataframe(
                self,
                None,
                self.newimages,
                self.individual_names,
                self.uniquebodyparts,
                self.multibodyparts,
            )
            self.dataFrame = pd.concat([self.dataFrame, self.df], axis=0)
            self.dataFrame.sort_index(inplace=True)
            # Rearrange bodypart columns in config order
            bodyparts = self.multibodyparts + self.uniquebodyparts
            self.dataFrame.reindex(
                bodyparts, axis=1, level=self.dataFrame.columns.names.index("bodyparts")
            )
        # Test whether there are missing frames and superfluous data
        if len(old_imgs) > len(self.relativeimagenames):
            missing_frames = set(old_imgs).difference(self.relativeimagenames)
            self.dataFrame.drop(missing_frames, inplace=True)

        # Check whether new labels were added
        self.new_multi = [x for x in self.multibodyparts if x not in self._old_multi]
        self.new_unique = [x for x in self.uniquebodyparts if x not in self._old_unique]

        # Checking if user added a new label
        if not any([self.new_multi, self.new_unique]):  # i.e. no new labels
            (
                self.figure,
                self.axes,
                self.canvas,
                self.toolbar,
                self.image_axis,
            ) = self.image_panel.drawplot(
                self.img,
                img_name,
                self.iter,
                self.index,
                self.multibodyparts,
                self.colormap,
                keep_view=self.view_locked,
            )
        else:
            # Found new labels in either multiple bodyparts or unique bodyparts
            dlg = wx.MessageDialog(
                None,
                "New label found in the config file. Do you want to see all the other labels?",
                "New label found",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                if self.new_multi:
                    self.multibodyparts = self.new_multi
                if self.new_unique:
                    self.uniquebodyparts = self.new_unique

            self.dataFrame = MainFrame.create_dataframe(
                self,
                self.dataFrame,
                self.relativeimagenames,
                self.individual_names,
                self.new_unique,
                self.new_multi,
            )
            (
                self.figure,
                self.axes,
                self.canvas,
                self.toolbar,
                self.image_axis,
            ) = self.image_panel.drawplot(
                self.img,
                img_name,
                self.iter,
                self.index,
                self.multibodyparts,
                self.colormap,
                keep_view=self.view_locked,
            )

        self.axes.callbacks.connect("xlim_changed", self.onZoom)
        self.axes.callbacks.connect("ylim_changed", self.onZoom)

        if self.individual_names[0] == "single":
            (
                self.choiceBox,
                self.individualrdb,
                self.rdb,
                self.change_marker_size,
                self.checkBox,
            ) = self.choice_panel.addRadioButtons(
                self.uniquebodyparts, self.individual_names, self.file, self.markerSize
            )
            self.image_panel.addcolorbar(
                self.img,
                self.image_axis,
                self.iter,
                self.uniquebodyparts,
                self.colormap,
            )
        else:
            (
                self.choiceBox,
                self.individualrdb,
                self.rdb,
                self.change_marker_size,
                self.checkBox,
            ) = self.choice_panel.addRadioButtons(
                self.multibodyparts, self.individual_names, self.file, self.markerSize
            )
            self.image_panel.addcolorbar(
                self.img, self.image_axis, self.iter, self.multibodyparts, self.colormap
            )
        self.individualrdb.Bind(wx.EVT_RADIOBOX, self.select_individual)
        # check if single is slected when radio buttons are changed
        if self.individualrdb.GetStringSelection() == "single":
            self.norm, self.colorIndex = self.image_panel.getColorIndices(
                self.img, self.uniquebodyparts
            )
        else:
            self.norm, self.colorIndex = self.image_panel.getColorIndices(
                self.img, self.multibodyparts
            )
        self.buttonCounter = MainFrame.plot(self, self.img)
        self.cidClick = self.canvas.mpl_connect("button_press_event", self.onClick)

        self.checkBox.Bind(wx.EVT_CHECKBOX, self.activateSlider)
        self.change_marker_size.Bind(wx.EVT_SLIDER, self.OnSliderScroll)