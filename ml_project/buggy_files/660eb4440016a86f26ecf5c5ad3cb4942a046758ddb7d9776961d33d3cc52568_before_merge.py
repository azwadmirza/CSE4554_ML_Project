def get_checkbox_style(color="#B5B5B5"):
    return """QCheckBox { color: %s; }
            QCheckBox::indicator:checked {image: url('%s'); width:16px; height:16px}
            QCheckBox::indicator:unchecked {image: url('%s'); width:16px; height:16px}
            """ % (color, get_image_path('checked-yes.png'), get_image_path('checked-no.png'))