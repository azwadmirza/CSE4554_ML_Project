        def forward(self, x):
            with torch.cuda.device(x.device):
                return super().forward(x)