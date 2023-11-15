    def forward(self, x):
        b = self.b
        return tt.log(b - x)