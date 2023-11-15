    def plot(self, orbit, label=None, color=None):
        """Plots state and osculating orbit in their plane.

        """
        if not self._frame:
            self.set_frame(*orbit.pqw())

        if (orbit, label) not in self._orbits:
            self._orbits.append((orbit, label))

        # if new attractor radius is smaller, plot it
        new_radius = max(orbit.attractor.R.to(u.km).value,
                         orbit.r_p.to(u.km).value / 6)
        if not self._attractor_radius:
            self.set_attractor(orbit)
        elif new_radius < self._attractor_radius:
            self.set_attractor(orbit)

        lines = []

        _, positions = orbit.sample(self.num_points)
        rr = positions.get_xyz().transpose()

        # Project on OrbitPlotter frame
        # x_vec, y_vec, z_vec = self._frame
        rr_proj = rr - rr.dot(self._frame[2])[:, None] * self._frame[2]
        x = rr_proj.dot(self._frame[0])
        y = rr_proj.dot(self._frame[1])

        # Plot current position
        l, = self.ax.plot(x[0].to(u.km).value, y[0].to(u.km).value,
                          'o', mew=0, color=color)
        lines.append(l)

        l, = self.ax.plot(x.to(u.km).value, y.to(u.km).value,
                          '--', color=l.get_color())
        lines.append(l)

        if label:
            # This will apply the label to either the point or the osculating
            # orbit depending on the last plotted line, as they share variable
            if not self.ax.get_legend():
                size = self.ax.figure.get_size_inches() + [8, 0]
                self.ax.figure.set_size_inches(size)
            orbit.epoch.out_subfmt = 'date_hm'
            label = '{} ({})'.format(orbit.epoch.iso, label)

            l.set_label(label)
            self.ax.legend(bbox_to_anchor=(1.05, 1), title="Names and epochs")

        self.ax.set_xlabel("$x$ (km)")
        self.ax.set_ylabel("$y$ (km)")
        self.ax.set_aspect(1)

        return lines