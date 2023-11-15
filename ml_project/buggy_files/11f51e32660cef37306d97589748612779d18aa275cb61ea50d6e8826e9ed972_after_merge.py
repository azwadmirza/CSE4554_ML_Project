    def update(self):
        super().update()
        if self.lifetime_elapsed <= self.in_duration:
            u = self.lifetime_elapsed / self.in_duration
            self.alpha = clamp(arcade.lerp(self.start_alpha, self.mid_alpha, u), 0 ,255)
        else:
            u = (self.lifetime_elapsed - self.in_duration) / self.out_duration
            self.alpha = clamp(arcade.lerp(self.mid_alpha, self.end_alpha, u), 0 ,255)