	def _show_text_with_options(self, cc, pl, text, text_x, text_y):
		cc.move_to(text_x, text_y)
		pl.set_text(text, -1)
		PangoCairo.update_layout(cc, pl)
		PangoCairo.show_layout(cc, pl)