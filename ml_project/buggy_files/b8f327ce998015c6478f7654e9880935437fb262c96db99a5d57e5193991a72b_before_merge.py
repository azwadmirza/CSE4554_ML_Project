    def on_debug_random_image_set(self, event):
        group_index = (
            0
            if len(self.__groupings) == 1
            else numpy.random.randint(0, len(self.__groupings) - 1, size=1)
        )
        keys, image_numbers = self.__groupings[group_index]
        if len(image_numbers) == 0:
            return
        numpy.random.seed()
        image_number_index = numpy.random.randint(1, len(image_numbers), size=1)[0]
        self.__within_group_index = (image_number_index - 1) % len(image_numbers)
        image_number = image_numbers[self.__within_group_index]
        self.__debug_measurements.next_image_set(image_number)
        self.debug_init_imageset()
        self.__debug_outlines = {}