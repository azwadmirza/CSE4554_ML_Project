    def _calculate_sprite_buffer(self):

        if self.is_static:
            usage = 'static'
        else:
            usage = 'stream'

        def calculate_pos_buffer():
            self._sprite_pos_data = array.array('f')
            # print("A")
            for sprite in self.sprite_list:
                self._sprite_pos_data.append(sprite.center_x)
                self._sprite_pos_data.append(sprite.center_y)

            self._sprite_pos_buf = shader.buffer(
                self._sprite_pos_data.tobytes(),
                usage=usage
            )
            variables = ['in_pos']
            self._sprite_pos_desc = shader.BufferDescription(
                self._sprite_pos_buf,
                '2f',
                variables,
                instanced=True)
            self._sprite_pos_changed = False

        def calculate_size_buffer():
            self._sprite_size_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_size_data.append(sprite.width)
                self._sprite_size_data.append(sprite.height)

            self._sprite_size_buf = shader.buffer(
                self._sprite_size_data.tobytes(),
                usage=usage
            )
            variables = ['in_size']
            self._sprite_size_desc = shader.BufferDescription(
                self._sprite_size_buf,
                '2f',
                variables,
                instanced=True)
            self._sprite_size_changed = False

        def calculate_angle_buffer():
            self._sprite_angle_data = array.array('f')
            for sprite in self.sprite_list:
                self._sprite_angle_data.append(math.radians(sprite.angle))

            self._sprite_angle_buf = shader.buffer(
                self._sprite_angle_data.tobytes(),
                usage=usage
            )
            variables = ['in_angle']
            self._sprite_angle_desc = shader.BufferDescription(
                self._sprite_angle_buf,
                '1f',
                variables,
                instanced=True)
            self._sprite_angle_changed = False

        def calculate_colors():
            self._sprite_color_data = array.array('B')
            for sprite in self.sprite_list:
                self._sprite_color_data.append(int(sprite.color[0]))
                self._sprite_color_data.append(int(sprite.color[1]))
                self._sprite_color_data.append(int(sprite.color[2]))
                self._sprite_color_data.append(int(sprite.alpha))

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

        def calculate_sub_tex_coords():

            new_array_of_texture_names = []
            new_array_of_images = []
            new_texture = False
            if self.array_of_images is None:
                new_texture = True

            # print()
            # print("New texture start: ", new_texture)

            for sprite in self.sprite_list:

                # noinspection PyProtectedMember
                if sprite.texture is None:
                    raise Exception("Error: Attempt to draw a sprite without a texture set.")

                name_of_texture_to_check = sprite.texture.name
                if name_of_texture_to_check not in self.array_of_texture_names:
                    new_texture = True
                    # print("New because of ", name_of_texture_to_check)

                if name_of_texture_to_check not in new_array_of_texture_names:
                    new_array_of_texture_names.append(name_of_texture_to_check)
                    image = sprite.texture.image
                    new_array_of_images.append(image)

            # print("New texture end: ", new_texture)
            # print(new_array_of_texture_names)
            # print(self.array_of_texture_names)
            # print()

            if new_texture:
                # Add back in any old textures. Chances are we'll need them.
                for index, old_texture_name in enumerate(self.array_of_texture_names):
                    if old_texture_name not in new_array_of_texture_names and self.array_of_images is not None:
                        new_array_of_texture_names.append(old_texture_name)
                        image = self.array_of_images[index]
                        new_array_of_images.append(image)

                self.array_of_texture_names = new_array_of_texture_names

                self.array_of_images = new_array_of_images
                # print(f"New Texture Atlas with names {self.array_of_texture_names}")

            # Get their sizes
            widths, heights = zip(*(i.size for i in self.array_of_images))

            # Figure out what size a composite would be
            total_width = sum(widths)
            max_height = max(heights)

            if new_texture:

                # TODO: This code isn't valid, but I think some releasing might be in order.
                # if self.texture is not None:
                #     shader.Texture.release(self.texture_id)

                # Make the composite image
                new_image = Image.new('RGBA', (total_width, max_height))

                x_offset = 0
                for image in self.array_of_images:
                    new_image.paste(image, (x_offset, 0))
                    x_offset += image.size[0]

                # Create a texture out the composite image
                texture_bytes = new_image.tobytes()
                self._texture = shader.texture(
                     (new_image.width, new_image.height),
                     4,
                     texture_bytes
                )

                if self.texture_id is None:
                    self.texture_id = SpriteList.next_texture_id

            # Create a list with the coordinates of all the unique textures
            tex_coords = []
            start_x = 0.0
            for image in self.array_of_images:
                end_x = start_x + (image.width / total_width)
                normalized_width = image.width / total_width
                start_height = 1 - (image.height / max_height)
                normalized_height = image.height / max_height
                tex_coords.append([start_x, start_height, normalized_width, normalized_height])
                start_x = end_x

            # Go through each sprite and pull from the coordinate list, the proper
            # coordinates for that sprite's image.
            array_of_sub_tex_coords = array.array('f')
            for sprite in self.sprite_list:
                index = self.array_of_texture_names.index(sprite.texture.name)
                for coord in tex_coords[index]:
                    array_of_sub_tex_coords.append(coord)

            self._sprite_sub_tex_buf = shader.buffer(
                array_of_sub_tex_coords.tobytes(),
                usage=usage
            )

            self._sprite_sub_tex_desc = shader.BufferDescription(
                self._sprite_sub_tex_buf,
                '4f',
                ['in_sub_tex_coords'],
                instanced=True)
            self._sprite_sub_tex_changed = False

        if len(self.sprite_list) == 0:
            return

        calculate_pos_buffer()
        calculate_size_buffer()
        calculate_angle_buffer()
        calculate_sub_tex_coords()
        calculate_colors()

        vertices = array.array('f', [
            #  x,    y,   u,   v
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ]
        )
        self.vbo_buf = shader.buffer(vertices.tobytes())
        vbo_buf_desc = shader.BufferDescription(
            self.vbo_buf,
            '2f 2f',
            ('in_vert', 'in_texture')
        )

        # Can add buffer to index vertices
        vao_content = [vbo_buf_desc,
                       self._sprite_pos_desc,
                       self._sprite_size_desc,
                       self._sprite_angle_desc,
                       self._sprite_sub_tex_desc,
                       self._sprite_color_desc]
        self._vao1 = shader.vertex_array(self.program, vao_content)