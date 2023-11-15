    def add_trajectory(
        self,
        positions,
        epochs,
        groundtrack_show=False,
        groundtrack_lead_time=None,
        groundtrack_trail_time=None,
        groundtrack_width=None,
        groundtrack_color=None,
        id_name=None,
        id_description=None,
        path_width=None,
        path_show=None,
        path_color=None,
        label_fill_color=None,
        label_outline_color=None,
        label_font=None,
        label_text=None,
        label_show=None,
    ):
        """
        Adds trajectory.

        Parameters
        ----------
        positions: ~astropy.coordinates.CartesianRepresentation
            Trajectory to plot.
        epochs: ~astropy.time.core.Time
            Epochs for positions.
        groundtrack_show: bool
            If set to true, the groundtrack is
            displayed.
        groundtrack_lead_time: double
            The time the animation is ahead of the real-time groundtrack
        groundtrack_trail_time: double
            The time the animation is behind the real-time groundtrack
        groundtrack_width: int
            Groundtrack width
        groundtrack_color: list (int)
            Rgba groundtrack color. By default, it is set to the path color
        id_name: str
            Set orbit name
        id_description: str
            Set orbit description
        path_width: int
            Path width
        path_show: bool
            Indicates whether the path is visible
        path_color: list (int)
            Rgba path color
        label_fill_color: list (int)
            Fill Color in rgba format
        label_outline_color: list (int)
            Outline Color in rgba format
        label_font: str
            Set label font style and size (CSS syntax)
        label_text: str
            Set label text
        label_show: bool
            Indicates whether the label is visible

        """

        if self.attractor is None:
            raise ValueError("An attractor must be set up first.")

        positions = (
            positions.represent_as(CartesianRepresentation).get_xyz(1).to(u.meter).value
        )

        epochs = Time(epochs, format="isot")

        if len(epochs) != len(positions):
            raise ValueError("Number of Points and Epochs must be equal.")

        epochs = np.fromiter(
            map(lambda epoch: (epoch - epochs[0]).to(u.second).value, epochs),
            dtype=float,
        )

        positions = np.around(
            np.concatenate([epochs[..., None], positions], axis=1).ravel(), 1
        ).tolist()

        self.trajectories.append([positions, None, label_text, path_color])

        start_epoch = Time(self.start_epoch, format="isot")

        pckt = Packet(
            id=self.i,
            name=id_name,
            description=id_description,
            availability=TimeInterval(start=self.start_epoch, end=self.end_epoch),
            position=Position(
                interpolationDegree=5,
                interpolationAlgorithm=InterpolationAlgorithms.LAGRANGE,
                referenceFrame=ReferenceFrames.INERTIAL,
                cartesian=positions,
                # Use explicit UTC timezone, rather than the default, which is a local timezone.
                epoch=start_epoch.datetime.replace(tzinfo=timezone.utc),
            ),
            path=Path(
                show=path_show,
                width=path_width,
                material=Material(
                    solidColor=SolidColorMaterial(color=Color.from_list(path_color))
                )
                if path_color is not None
                else Material(
                    solidColor=SolidColorMaterial(color=Color.from_list([255, 255, 0]))
                ),
                resolution=120,
            ),
            label=Label(
                text=label_text,
                font=label_font if label_font is not None else "11pt Lucida Console",
                show=label_show,
                fillColor=Color(rgba=label_fill_color)
                if label_fill_color is not None
                else Color(rgba=[255, 255, 0, 255]),
                outlineColor=Color(rgba=label_outline_color)
                if label_outline_color is not None
                else Color(rgba=[255, 255, 0, 255]),
            ),
            billboard=Billboard(image=PIC_SATELLITE, show=True),
        )

        self.packets.append(pckt)

        if groundtrack_show:
            raise NotImplementedError(
                "Ground tracking for trajectory not implemented yet"
            )

        self.i += 1