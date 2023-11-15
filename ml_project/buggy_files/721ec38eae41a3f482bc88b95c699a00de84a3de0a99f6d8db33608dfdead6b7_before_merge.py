    def update_subscribe_button(self):
        if self.channel_info["subscribed"]:
            self.subscribe_button.setIcon(QIcon(QPixmap(get_image_path('subscribed_yes.png'))))
        else:
            self.subscribe_button.setIcon(QIcon(QPixmap(get_image_path('subscribed_not.png'))))

        self.num_subs_label.setText(str(self.channel_info["votes"]))