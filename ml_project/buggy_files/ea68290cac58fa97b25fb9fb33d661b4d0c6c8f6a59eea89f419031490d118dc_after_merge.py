    def update_position(self, sprite: Sprite):
        """
        Called by the Sprite class to update position, angle, size and color
        of the specified sprite.
        Necessary for batch drawing of items.

        :param Sprite sprite: Sprite to update.
        """
        if self._vao1 is None:
            return

        i = self.sprite_idx[sprite]

        self._sprite_pos_data[i * 2] = sprite.position[0]
        self._sprite_pos_data[i * 2 + 1] = sprite.position[1]
        self._sprite_pos_changed = True

        self._sprite_angle_data[i] = math.radians(sprite.angle)
        self._sprite_angle_changed = True

        self._sprite_color_data[i * 4] = int(sprite.color[0])
        self._sprite_color_data[i * 4 + 1] = int(sprite.color[1])
        self._sprite_color_data[i * 4 + 2] = int(sprite.color[2])
        self._sprite_color_data[i * 4 + 3] = int(sprite.alpha)
        self._sprite_color_changed = True