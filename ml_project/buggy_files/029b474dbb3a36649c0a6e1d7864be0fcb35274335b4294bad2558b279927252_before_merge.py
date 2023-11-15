    def post_group(self, workspace, *args):
        if (self.when_to_save == WS_LAST_CYCLE and 
            self.save_image_or_figure != IF_MOVIE):
            self.save_image(workspace)