    def __init__(self, desired_tile_form='RGB', user_agent='cartopybot/1.0'):
        self.imgs = []
        self.crs = ccrs.Mercator.GOOGLE
        self.desired_tile_form = desired_tile_form
        self.user_agent = user_agent