        def calculate_colors():
            self._sprite_color_data = array.array('B')
            for sprite in self.sprite_list:
                self._sprite_color_data.append(sprite.color[0])
                self._sprite_color_data.append(sprite.color[1])
                self._sprite_color_data.append(sprite.color[2])
                self._sprite_color_data.append(sprite.alpha)

            self._sprite_color_buf = shader.buffer(
                self._sprite_color_data.tobytes(),
                usage=usage
            )
            variables = ['in_color']
            self._sprite_color_desc = shader.BufferDescription(
                self._sprite_color_buf,
                '4B',
                variables,
                normalized=['in_color'], instanced=True)
            self._sprite_color_changed = False