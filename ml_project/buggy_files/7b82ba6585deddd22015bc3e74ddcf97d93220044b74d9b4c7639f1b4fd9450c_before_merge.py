    def __init__(self, desired_tile_form='RGB'):
        self.imgs = []
        self.crs = ccrs.Mercator.GOOGLE
        self.desired_tile_form = desired_tile_form