    def startup(self, **kwargs):
        self.state = "normal"

        # this sprite is used to display the item
        # its also animated to pop out of the backpack
        self.item_center = self.rect.width * .164, self.rect.height * .13
        self.item_sprite = Sprite()
        self.item_sprite.image = None
        self.sprites.add(self.item_sprite)

        # do not move this line
        super(ItemMenuState, self).startup(**kwargs)
        self.menu_items.line_spacing = tools.scale(5)

        # this is the area where the item description is displayed
        rect = self.game.screen.get_rect()
        rect.top = tools.scale(106)
        rect.left = tools.scale(3)
        rect.width = tools.scale(250)
        rect.height = tools.scale(32)
        self.text_area = TextArea(self.font, self.font_color, (96, 96, 128))
        print(rect)
        self.text_area.rect = rect
        self.sprites.add(self.text_area, layer=100)

        # load the backpack icon
        self.backpack_center = self.rect.width * .16, self.rect.height * .45
        self.load_sprite("gfx/ui/item/backpack.png", center=self.backpack_center, layer=100)