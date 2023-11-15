    def update(self):
        """Advance the Particle's simulation"""
        super().update()
        a = arcade.utils.lerp(self.start_alpha,
                              self.end_alpha,
                              self.lifetime_elapsed / self.lifetime_original)
        self.alpha = clamp(a, 0, 255)