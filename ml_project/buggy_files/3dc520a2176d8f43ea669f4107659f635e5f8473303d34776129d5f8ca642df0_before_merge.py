    def forward(self, x):
        b = self.b
        r = tt.log(b - x)
        return r