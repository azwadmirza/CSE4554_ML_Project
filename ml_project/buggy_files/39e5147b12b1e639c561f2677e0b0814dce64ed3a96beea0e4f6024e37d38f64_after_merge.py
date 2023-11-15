    def __init__(self, parent, workspace):
        self.frame = WorkspaceViewFigure(
            parent,
            title="CellProfiler Workspace",
            secret_panel_class=wx.lib.scrolledpanel.ScrolledPanel,
            help_menu_items=FIGURE_HELP,
        )
        self.workspace = workspace
        self.ignore_redraw = False
        self.image_rows = []
        self.object_rows = []
        self.mask_rows = []
        self.measurement_rows = []
        self.frame.set_subplots((1, 1))
        self.axes = self.frame.subplot(0, 0)
        self.axes.invert_yaxis()
        interpolation = get_interpolation_mode()
        if interpolation == IM_NEAREST:
            interpolation = INTERPOLATION_NEAREST
        elif interpolation == IM_BILINEAR:
            interpolation = INTERPOLATION_BILINEAR
        else:
            interpolation = INTERPOLATION_BICUBIC
        self.image = CPImageArtist(interpolation=interpolation)
        assert isinstance(self.axes, matplotlib.axes.Axes)
        self.axes.add_artist(self.image)
        self.axes.set_aspect("equal")
        self.__axes_scale = None

        panel = self.frame.secret_panel
        panel.Sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel = panel
        #
        # Make a grid of image controls
        #
        panel.Sizer.AddSpacer(4)
        self.image_grid = wx.GridBagSizer(vgap=3, hgap=3)
        sub_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.Sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 3)
        sub_sizer.Add(self.image_grid, 0, wx.ALIGN_LEFT)
        self.image_grid.Add(
            wx.StaticText(panel, label="Images"),
            (0, C_CHOOSER),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.image_grid.Add(
            wx.StaticText(panel, label="Color"),
            (0, C_COLOR),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.image_grid.Add(
            wx.StaticText(panel, label="Show"),
            (0, C_SHOW),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.image_grid.Add(
            wx.StaticText(panel, label="Remove"),
            (0, C_REMOVE),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.add_image_row(can_delete=False)
        add_image_button = wx.Button(panel, label="Add Image")
        sub_sizer.Add(add_image_button, 0, wx.ALIGN_RIGHT)
        add_image_button.Bind(wx.EVT_BUTTON, lambda event: self.add_image_row())
        panel.Sizer.AddSpacer(4)
        panel.Sizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND)
        panel.Sizer.AddSpacer(4)
        #
        # Make a grid of object controls
        #
        self.object_grid = wx.GridBagSizer(vgap=3, hgap=3)
        sub_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.Sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 3)
        sub_sizer.Add(self.object_grid, 0, wx.ALIGN_LEFT)
        self.object_grid.Add(
            wx.StaticText(panel, label="Objects"),
            (0, C_CHOOSER),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.object_grid.Add(
            wx.StaticText(panel, label="Color"),
            (0, C_COLOR),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.object_grid.Add(
            wx.StaticText(panel, label="Show"),
            (0, C_SHOW),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.object_grid.Add(
            wx.StaticText(panel, label="Remove"),
            (0, C_REMOVE),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.add_objects_row(can_delete=False)
        add_object_button = wx.Button(panel, label="Add Objects")
        sub_sizer.Add(add_object_button, 0, wx.ALIGN_RIGHT)
        add_object_button.Bind(wx.EVT_BUTTON, lambda event: self.add_objects_row())
        panel.Sizer.AddSpacer(4)
        panel.Sizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND)
        panel.Sizer.AddSpacer(4)
        #
        # Make a grid of mask controls
        #
        self.mask_grid = wx.GridBagSizer(vgap=3, hgap=3)
        sub_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.Sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 3)
        sub_sizer.Add(self.mask_grid, 0, wx.ALIGN_LEFT)
        self.mask_grid.Add(
            wx.StaticText(panel, label="Masks"),
            (0, C_CHOOSER),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.mask_grid.Add(
            wx.StaticText(panel, label="Color"),
            (0, C_COLOR),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.mask_grid.Add(
            wx.StaticText(panel, label="Show"),
            (0, C_SHOW),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.mask_grid.Add(
            wx.StaticText(panel, label="Remove"),
            (0, C_REMOVE),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.add_mask_row(can_delete=False)
        add_mask_button = wx.Button(panel, label="Add Mask")
        sub_sizer.Add(add_mask_button, 0, wx.ALIGN_RIGHT)
        add_mask_button.Bind(wx.EVT_BUTTON, lambda event: self.add_mask_row())
        panel.Sizer.AddSpacer(4)
        panel.Sizer.Add(wx.StaticLine(panel, style=wx.LI_HORIZONTAL), 0, wx.EXPAND)
        panel.Sizer.AddSpacer(4)
        #
        # Make a grid of measurements to display
        #
        self.m_grid = wx.GridBagSizer(vgap=3, hgap=3)
        sub_sizer = wx.BoxSizer(wx.VERTICAL)
        panel.Sizer.Add(sub_sizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 3)
        sub_sizer.Add(self.m_grid, 0, wx.ALIGN_LEFT)
        self.m_grid.Add(
            wx.StaticText(panel, label="Measurement"),
            (0, C_CHOOSER),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.m_grid.Add(
            wx.StaticText(panel, label="Font"),
            (0, C_COLOR),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.m_grid.Add(
            wx.StaticText(panel, label="Show"),
            (0, C_SHOW),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.m_grid.Add(
            wx.StaticText(panel, label="Remove"),
            (0, C_REMOVE),
            flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM,
        )
        self.add_measurement_row(can_delete=False)
        add_measurement_button = wx.Button(panel, label="Add Measurement")
        sub_sizer.Add(add_measurement_button, 0, wx.ALIGN_RIGHT)
        add_measurement_button.Bind(wx.EVT_BUTTON, self.on_add_measurement_row)
        panel.Sizer.AddSpacer(6)
        help_button = wx.Button(panel, wx.ID_HELP)
        panel.Sizer.Add(help_button, 0, wx.ALIGN_RIGHT)

        def on_help(event):
            HTMLDialog(
                panel,
                "Workspace viewer help",
                rst_to_html_fragment(WORKSPACE_VIEWER_HELP),
            ).Show()

        help_button.Bind(wx.EVT_BUTTON, on_help)
        self.image.add_to_menu(self.frame, self.frame.menu_subplots)
        self.frame.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
        self.frame.Bind(wx.EVT_CLOSE, self.on_frame_close)
        self.set_workspace(workspace)
        self.frame.secret_panel.Show()
        w, h = self.frame.GetSize()
        w += self.frame.secret_panel.GetMinWidth()
        self.frame.SetSize(wx.Size(w, h))