    def set_position(self, center_x: float, center_y: float):
        """
        Set a sprite's position

        >>> import arcade
        >>> empty_sprite = arcade.Sprite()
        >>> empty_sprite.set_position(10, 10)
        """
        self.center_x = center_x
        self.center_y = center_y