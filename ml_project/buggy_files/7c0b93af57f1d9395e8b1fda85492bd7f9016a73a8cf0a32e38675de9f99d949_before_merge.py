    def forward(self, x):
        a = self.a
        r = tt.log(x - a)
        return r