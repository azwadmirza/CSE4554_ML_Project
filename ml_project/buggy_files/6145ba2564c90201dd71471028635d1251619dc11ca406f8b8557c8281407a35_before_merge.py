    def __init__(self, width, height):
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.AMAZON)

        self.pause = False
        self.coin_list = None
        self.button_list = None