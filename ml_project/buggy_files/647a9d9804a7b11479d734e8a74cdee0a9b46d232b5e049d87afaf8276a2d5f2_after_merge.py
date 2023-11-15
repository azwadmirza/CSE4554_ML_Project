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
        dlg.Destroy()

        # Enabling the zoom, pan and home buttons
        self.zoom.Enable(True)
        self.home.Enable(True)
        self.pan.Enable(True)
        self.lock.Enable(True)

        # Reading config file and its variables
        self.cfg = auxiliaryfunctions.read_config(self.config_file)
        self.scorer = self.cfg["scorer"]
        self.bodyparts = self.cfg["bodyparts"]
        self.videos = self.cfg["video_sets"].keys()
        self.markerSize = self.cfg["dotsize"]
        self.alpha = self.cfg["alphavalue"]
        self.colormap = plt.get_cmap(self.cfg["colormap"])
        self.colormap = self.colormap.reversed()
        self.project_path = self.cfg["project_path"]

        imlist = []
        for imtype in self.imtypes:
            imlist.extend(
                [
                    fn
                    for fn in glob.glob(os.path.join(self.dir, imtype))
                    if ("labeled.png" not in fn)
                ]
            )

        if len(imlist) == 0:
            print("No images found!!")

        self.index = np.sort(imlist)
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
            self.dataFrame.sort_index(inplace=True)
            self.prev.Enable(True)

            # Finds the first empty row in the dataframe and sets the iteration to that index
            for idx, j in enumerate(self.dataFrame.index):
                values = self.dataFrame.loc[j, :].values
                if np.prod(np.isnan(values)) == 1:
                    self.iter = idx
                    break
                else:
                    self.iter = 0

        except:
            a = np.empty((len(self.index), 2))
            a[:] = np.nan
            for bodypart in self.bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ["x", "y"]],
                    names=["scorer", "bodyparts", "coords"],
                )
                frame = pd.DataFrame(a, columns=index, index=self.relativeimagenames)
                self.dataFrame = pd.concat([self.dataFrame, frame], axis=1)
            self.iter = 0

        # Reading the image name
        self.img = self.dataFrame.index[self.iter]
        img_name = Path(self.img).name
        self.norm, self.colorIndex = self.image_panel.getColorIndices(
            self.img, self.bodyparts
        )

        # Checking for new frames and adding them to the existing dataframe
        old_imgs = np.sort(list(self.dataFrame.index))
        self.newimages = list(set(self.relativeimagenames) - set(old_imgs))
        if self.newimages == []:
            pass
        else:
            print("Found new frames..")
            # Create an empty dataframe with all the new images and then merge this to the existing dataframe.
            self.df = None
            a = np.empty((len(self.newimages), 2))
            a[:] = np.nan
            for bodypart in self.bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ["x", "y"]],
                    names=["scorer", "bodyparts", "coords"],
                )
                frame = pd.DataFrame(a, columns=index, index=self.newimages)
                self.df = pd.concat([self.df, frame], axis=1)
            self.dataFrame = pd.concat([self.dataFrame, self.df], axis=0)
            # Sort it by the index values
            self.dataFrame.sort_index(inplace=True)

        # checks for unique bodyparts
        if len(self.bodyparts) != len(set(self.bodyparts)):
            print(
                "Error - bodyparts must have unique labels! Please choose unique bodyparts in config.yaml file and try again. Quitting for now!"
            )
            self.Close(True)

        # Extracting the list of new labels
        oldBodyParts = self.dataFrame.columns.get_level_values(1)
        _, idx = np.unique(oldBodyParts, return_index=True)
        oldbodyparts2plot = list(oldBodyParts[np.sort(idx)])
        self.new_bodyparts = [x for x in self.bodyparts if x not in oldbodyparts2plot]
        # Checking if user added a new label
        if self.new_bodyparts == []:  # i.e. no new label
            (
                self.figure,
                self.axes,
                self.canvas,
                self.toolbar,
            ) = self.image_panel.drawplot(
                self.img, img_name, self.iter, self.index, self.bodyparts, self.colormap
            )
            self.axes.callbacks.connect("xlim_changed", self.onZoom)
            self.axes.callbacks.connect("ylim_changed", self.onZoom)

            (
                self.choiceBox,
                self.rdb,
                self.slider,
                self.checkBox,
            ) = self.choice_panel.addRadioButtons(
                self.bodyparts, self.file, self.markerSize
            )
            self.buttonCounter = MainFrame.plot(self, self.img)
            self.cidClick = self.canvas.mpl_connect("button_press_event", self.onClick)
            self.canvas.mpl_connect("button_release_event", self.onButtonRelease)
        else:
            dlg = wx.MessageDialog(
                None,
                "New label found in the config file. Do you want to see all the other labels?",
                "New label found",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                self.bodyparts = self.new_bodyparts
                self.norm, self.colorIndex = self.image_panel.getColorIndices(
                    self.img, self.bodyparts
                )
            a = np.empty((len(self.index), 2))
            a[:] = np.nan
            for bodypart in self.new_bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ["x", "y"]],
                    names=["scorer", "bodyparts", "coords"],
                )
                frame = pd.DataFrame(a, columns=index, index=self.relativeimagenames)
                self.dataFrame = pd.concat([self.dataFrame, frame], axis=1)

            (
                self.figure,
                self.axes,
                self.canvas,
                self.toolbar,
            ) = self.image_panel.drawplot(
                self.img, img_name, self.iter, self.index, self.bodyparts, self.colormap
            )
            self.axes.callbacks.connect("xlim_changed", self.onZoom)
            self.axes.callbacks.connect("ylim_changed", self.onZoom)

            (
                self.choiceBox,
                self.rdb,
                self.slider,
                self.checkBox,
            ) = self.choice_panel.addRadioButtons(
                self.bodyparts, self.file, self.markerSize
            )
            self.cidClick = self.canvas.mpl_connect("button_press_event", self.onClick)
            self.canvas.mpl_connect("button_release_event", self.onButtonRelease)
            self.buttonCounter = MainFrame.plot(self, self.img)

        self.checkBox.Bind(wx.EVT_CHECKBOX, self.activateSlider)
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll)