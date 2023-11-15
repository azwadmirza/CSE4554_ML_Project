    def _update_camera(self):
        if self.viewer.dims.ndisplay == 3:
            # Set a 3D camera
            if not isinstance(self.view.camera, ArcballCamera):
                self.view.camera = ArcballCamera(name="ArcballCamera")
                # flip y-axis to have correct alignment
                # self.view.camera.flip = (0, 1, 0)

                self.view.camera.viewbox_key_event = viewbox_key_event
                self.viewer.reset_view()
        else:
            # Set 2D camera
            if not isinstance(self.view.camera, PanZoomCamera):
                self.view.camera = PanZoomCamera(
                    aspect=1, name="PanZoomCamera"
                )
                # flip y-axis to have correct alignment
                self.view.camera.flip = (0, 1, 0)

                self.view.camera.viewbox_key_event = viewbox_key_event
                self.viewer.reset_view()