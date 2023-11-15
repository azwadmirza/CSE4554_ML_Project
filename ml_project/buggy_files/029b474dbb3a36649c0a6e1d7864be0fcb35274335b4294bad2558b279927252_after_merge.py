    def post_group(self, workspace, *args):
        if (self.when_to_save == WS_LAST_CYCLE and 
            self.save_image_or_figure != IF_MOVIE):
            if self.save_image_or_figure == IF_OBJECTS:
                self.save_objects(workspace)
            else:
                self.save_image(workspace)