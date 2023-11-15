    def update(self):
        """Advance the Particle's simulation"""
        super().update()
        self.alpha = arcade.utils.lerp(self.start_alpha, self.end_alpha, self.lifetime_elapsed / self.lifetime_original)