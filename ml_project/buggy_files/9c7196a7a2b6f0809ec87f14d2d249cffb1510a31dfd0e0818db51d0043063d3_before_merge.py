    def select_point(self, event, radius=5):

        """
        Get line point close to mouse pointer and its index

        Parameters
        ----------
        event : the mouse event being processed
        radius : scalar
            max. distance in pixels between mouse and line point to be accepted
        return: (numpy.array, int)
            picked point and index of the point in the pos array
        """

        # position in scene/document coordinates
        pos_scene = event.pos[:3]

        # project mouse radius from screen coordinates to document coordinates
        mouse_radius = \
            (event.visual_to_canvas.imap(np.array([radius, radius, radius])) -
             event.visual_to_canvas.imap(np.array([0, 0, 0])))[0]
        # print("Mouse radius in document units: ", mouse_radius)

        # find first point within mouse_radius
        index = 0
        for p in self.pos:
            if np.linalg.norm(pos_scene - p) < mouse_radius:
                # print p, index
                # point found, return point and its index
                return p, index
            index += 1
        # no point found, return None
        return None, -1