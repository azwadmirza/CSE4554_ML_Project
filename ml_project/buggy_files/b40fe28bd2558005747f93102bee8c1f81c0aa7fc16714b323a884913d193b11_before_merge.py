    def add_image(self, image, image_name):
        self[image_name] = image
        self.update_attributes()