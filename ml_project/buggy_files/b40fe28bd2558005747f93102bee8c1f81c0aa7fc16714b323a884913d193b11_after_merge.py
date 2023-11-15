    def add_image(self, image: Image, image_name: str) -> None:
        self[image_name] = image
        self.update_attributes()