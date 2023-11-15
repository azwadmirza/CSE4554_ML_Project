    def handle_interaction(self, current_shape, orig_image):
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        import wx
        """Show the cropping user interface"""
        pixel_data = stretch(orig_image)
        #
        # Create the UI - a dialog with a figure inside
        #
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        dialog_box = wx.Dialog(wx.GetApp().TopWindow, -1,
                               "Select the cropping region",
                               size=(640, 480),
                               style=style)
        sizer = wx.BoxSizer(wx.VERTICAL)
        figure = matplotlib.figure.Figure()
        panel = FigureCanvasWxAgg(dialog_box, -1, figure)
        sizer.Add(panel, 1, wx.EXPAND)
        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(dialog_box, wx.ID_OK))
        btn_sizer.AddButton(wx.Button(dialog_box, wx.ID_CANCEL))
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        dialog_box.SetSizer(sizer)
        dialog_box.Size = dialog_box.BestSize
        dialog_box.Layout()

        axes = figure.add_subplot(1, 1, 1)
        assert isinstance(axes, matplotlib.axes.Axes)
        if pixel_data.ndim == 2:
            axes.imshow(pixel_data, matplotlib.cm.Greys_r, origin="upper")
        else:
            axes.imshow(pixel_data, origin="upper")
        # t = axes.transData.inverted()
        current_handle = [None]

        def data_xy(mouse_event):
            """Return the mouse event's x & y converted into data-relative coords"""
            x = mouse_event.xdata
            y = mouse_event.ydata
            return x, y

        class Handle(matplotlib.patches.Rectangle):
            dm = max((10, min(pixel_data.shape) / 50))
            height, width = (dm, dm)

            def __init__(self, x, y, on_move):
                x = max(0, min(x, pixel_data.shape[1]))
                y = max(0, min(y, pixel_data.shape[0]))
                self.__selected = False
                self.__color = cellprofiler.preferences.get_primary_outline_color()
                self.__color = numpy.hstack((self.__color, [255])).astype(float) / 255.0
                self.__on_move = on_move
                super(Handle, self).__init__((x - self.width / 2, y - self.height / 2),
                                             self.width, self.height,
                                             edgecolor=self.__color,
                                             facecolor="none")
                self.set_picker(True)

            def move(self, x, y):
                self.set_xy((x - self.width / 2, y - self.height / 2))
                self.__on_move(x, y)

            def select(self, on):
                self.__selected = on
                if on:
                    current_handle[0] = self
                    self.set_facecolor(self.__color)

                else:
                    self.set_facecolor("none")
                    if current_handle[0] == self:
                        current_handle[0] = None
                figure.canvas.draw()
                dialog_box.Update()

            @property
            def is_selected(self):
                return self.__selected

            @property
            def center_x(self):
                """The handle's notion of its x coordinate"""
                return self.get_x() + self.get_width() / 2

            @property
            def center_y(self):
                """The handle's notion of its y coordinate"""
                return self.get_y() + self.get_height() / 2

            def handle_pick(self, event):
                mouse_event = event.mouseevent
                x, y = data_xy(mouse_event)
                if mouse_event.button == 1:
                    self.select(True)
                    self.orig_x = self.center_x
                    self.orig_y = self.center_y
                    self.first_x = x
                    self.first_y = y

            def handle_mouse_move_event(self, event):
                x, y = data_xy(event)
                if x is None or y is None:
                    return
                x = x - self.first_x + self.orig_x
                y = y - self.first_y + self.orig_y
                if x < 0:
                    x = 0
                if x >= pixel_data.shape[1]:
                    x = pixel_data.shape[1] - 1
                if y < 0:
                    y = 0
                if y >= pixel_data.shape[0]:
                    y = pixel_data.shape[0] - 1
                self.move(x, y)

        class CropRectangle(object):
            def __init__(self, top_left, bottom_right):
                self.__left, self.__top = top_left
                self.__right, self.__bottom = bottom_right
                color = cellprofiler.preferences.get_primary_outline_color()
                color = numpy.hstack((color, [255])).astype(float) / 255.0
                self.rectangle = matplotlib.patches.Rectangle(
                        (min(self.__left, self.__right),
                         min(self.__bottom, self.__top)),
                        abs(self.__right - self.__left),
                        abs(self.__top - self.__bottom),
                        edgecolor=color,
                        facecolor="none"
                )
                self.top_left_handle = Handle(top_left[0], top_left[1],
                                              self.handle_top_left)
                self.bottom_right_handle = Handle(bottom_right[0],
                                                  bottom_right[1],
                                                  self.handle_bottom_right)

            def handle_top_left(self, x, y):
                self.__left = x
                self.__top = y
                self.__reshape()

            def handle_bottom_right(self, x, y):
                self.__right = x
                self.__bottom = y
                self.__reshape()

            def __reshape(self):
                self.rectangle.set_xy((min(self.__left, self.__right),
                                       min(self.__bottom, self.__top)))
                self.rectangle.set_width(abs(self.__right - self.__left))
                self.rectangle.set_height(abs(self.__bottom - self.__top))
                self.rectangle.figure.canvas.draw()
                dialog_box.Update()

            @property
            def patches(self):
                return [self.rectangle, self.top_left_handle,
                        self.bottom_right_handle]

            @property
            def handles(self):
                return [self.top_left_handle, self.bottom_right_handle]

            @property
            def left(self):
                return min(self.__left, self.__right)

            @property
            def right(self):
                return max(self.__left, self.__right)

            @property
            def top(self):
                return min(self.__top, self.__bottom)

            @property
            def bottom(self):
                return max(self.__top, self.__bottom)

        class CropEllipse(object):
            def __init__(self, center, radius):
                """Draw an ellipse with control points at the ellipse center and
                a given x and y radius"""
                self.center_x, self.center_y = center
                self.radius_x = self.center_x + radius[0] / 2
                self.radius_y = self.center_y + radius[1] / 2
                color = cellprofiler.preferences.get_primary_outline_color()
                color = numpy.hstack((color, [255])).astype(float) / 255.0
                self.ellipse = matplotlib.patches.Ellipse(center, self.width, self.height,
                                                          edgecolor=color,
                                                          facecolor="none")
                self.center_handle = Handle(self.center_x, self.center_y,
                                            self.move_center)
                self.radius_handle = Handle(self.radius_x, self.radius_y,
                                            self.move_radius)

            def move_center(self, x, y):
                self.center_x = x
                self.center_y = y
                self.redraw()

            def move_radius(self, x, y):
                self.radius_x = x
                self.radius_y = y
                self.redraw()

            @property
            def width(self):
                return abs(self.center_x - self.radius_x) * 4

            @property
            def height(self):
                return abs(self.center_y - self.radius_y) * 4

            def redraw(self):
                self.ellipse.center = (self.center_x, self.center_y)
                self.ellipse.width = self.width
                self.ellipse.height = self.height
                self.ellipse.figure.canvas.draw()
                dialog_box.Update()

            @property
            def patches(self):
                return [self.ellipse, self.center_handle, self.radius_handle]

            @property
            def handles(self):
                return [self.center_handle, self.radius_handle]

        if self.shape == SH_ELLIPSE:
            if current_shape is None:
                current_shape = {
                    EL_XCENTER: pixel_data.shape[1] / 2,
                    EL_YCENTER: pixel_data.shape[0] / 2,
                    EL_XRADIUS: pixel_data.shape[1] / 2,
                    EL_YRADIUS: pixel_data.shape[0] / 2
                }
            ellipse = current_shape
            shape = CropEllipse((ellipse[EL_XCENTER], ellipse[EL_YCENTER]),
                                (ellipse[EL_XRADIUS], ellipse[EL_YRADIUS]))
        else:
            if current_shape is None:
                current_shape = {
                    RE_LEFT: pixel_data.shape[1] / 4,
                    RE_TOP: pixel_data.shape[0] / 4,
                    RE_RIGHT: pixel_data.shape[1] * 3 / 4,
                    RE_BOTTOM: pixel_data.shape[0] * 3 / 4
                }
            rectangle = current_shape
            shape = CropRectangle((rectangle[RE_LEFT], rectangle[RE_TOP]),
                                  (rectangle[RE_RIGHT], rectangle[RE_BOTTOM]))
        for patch in shape.patches:
            axes.add_artist(patch)

        def on_mouse_down_event(event):
            axes.pick(event)

        def on_mouse_move_event(event):
            if current_handle[0] is not None:
                current_handle[0].handle_mouse_move_event(event)

        def on_mouse_up_event(event):
            if current_handle[0] is not None:
                current_handle[0].select(False)

        def on_pick_event(event):
            for h in shape.handles:
                if id(h) == id(event.artist):
                    h.handle_pick(event)

        figure.canvas.mpl_connect('button_press_event', on_mouse_down_event)
        figure.canvas.mpl_connect('button_release_event', on_mouse_up_event)
        figure.canvas.mpl_connect('motion_notify_event', on_mouse_move_event)
        figure.canvas.mpl_connect('pick_event', on_pick_event)

        try:
            if dialog_box.ShowModal() != wx.ID_OK:
                raise ValueError("Cancelled by user")
        finally:
            dialog_box.Destroy()
        if self.shape == SH_RECTANGLE:
            return {
                RE_LEFT: shape.left,
                RE_TOP: shape.top,
                RE_RIGHT: shape.right,
                RE_BOTTOM: shape.bottom
            }
        else:
            return {
                EL_XCENTER: shape.center_x,
                EL_YCENTER: shape.center_y,
                EL_XRADIUS: shape.width / 2,
                EL_YRADIUS: shape.height / 2
            }