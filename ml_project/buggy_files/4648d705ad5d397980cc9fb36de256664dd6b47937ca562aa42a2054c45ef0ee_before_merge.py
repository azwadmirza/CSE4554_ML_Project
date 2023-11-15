    def on_click(self, pos: Vec2, button: int, action: int) -> bool:
        if action == glfw.GLFW_PRESS:
            clicked_handle = self.get_handle_at(pos)
            if clicked_handle != self.active_handle:
                self.active_handle = clicked_handle
                return True
        elif action == glfw.GLFW_RELEASE:
            if self.active_handle != Handle.NONE:
                self.active_handle = Handle.NONE
                return True
        return False