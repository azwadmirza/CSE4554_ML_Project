    def on_debug_random_image_set(self, event):
        keys, image_numbers = self.__groupings[self.__grouping_index]
        numpy.random.seed()
        if len(image_numbers) == 0:
            return
        elif len(image_numbers) == 1:
            self.__within_group_index = 0
        else:
            self.__within_group_index = numpy.random.randint(0, len(image_numbers))
        image_number = image_numbers[self.__within_group_index]
        self.__debug_measurements.next_image_set(image_number)
        self.debug_init_imageset()
        self.__debug_outlines = {}