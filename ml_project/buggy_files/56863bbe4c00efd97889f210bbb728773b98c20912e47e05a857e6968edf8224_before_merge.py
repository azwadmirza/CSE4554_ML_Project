    def initialize_with_channel(self, channel):
        self.channel_info = channel

        self.subscribe_button = self.findChild(QWidget, "subscribe_button")
        self.num_subs_label = self.findChild(QWidget, "num_subs_label")

        self.subscribe_button.clicked.connect(self.on_subscribe_button_click)
        self.update_subscribe_button()