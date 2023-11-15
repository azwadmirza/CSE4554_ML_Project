    def animate_open(self):
        """ Animate the menu sliding in

        :return:
        """
        self.state = "opening"  # required

        # position the menu off screen.  it will be slid into view with an animation
        right, height = prepare.SCREEN_SIZE

        # TODO: more robust API for sizing (kivy esque?)
        # this is highly irregular:
        # shrink to get the final width
        # record the width
        # turn off shrink, then adjust size
        self.shrink_to_items = True     # force shrink of menu
        self.menu_items.expand = False  # force shrink of items
        self.refresh_layout()           # rearrange items
        width = self.rect.width         # store the ideal width

        self.shrink_to_items = False    # force shrink of menu
        self.menu_items.expand = True   # force shrink of items
        self.refresh_layout()           # rearrange items
        self.rect = pygame.Rect(right, 0, width, height)  # set new rect

        # animate the menu sliding in
        ani = self.animate(self.rect, x=right - width, duration=.50)
        ani.callback = lambda: setattr(self, "state", "normal")
        return ani