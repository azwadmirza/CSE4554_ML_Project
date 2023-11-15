    def select_point(self, pos_scene, radius=5):

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

        # project mouse radius from screen coordinates to document coordinates

        mouse_radius = 6
        # print("Mouse radius in document units: ", mouse_radius)

        # find first point within mouse_radius
        index = 0
        for p in self.pos:
            if np.linalg.norm(pos_scene[:3] - p) < mouse_radius:
                # print p, index
                # point found, return point and its index
                return p, index
            index += 1
        # no point found, return None
        return None, -1