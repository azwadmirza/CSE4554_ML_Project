    def update(self):
        """
        Update the sprite.
        """
        self.position = [self._position[0] + self.change_x, self._position[1] + self.change_y]
        self.angle += self.change_angle