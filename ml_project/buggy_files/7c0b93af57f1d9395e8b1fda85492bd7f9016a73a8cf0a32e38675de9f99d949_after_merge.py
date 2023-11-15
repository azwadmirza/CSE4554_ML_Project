    def forward(self, x):
        a = self.a
        return tt.log(x - a)