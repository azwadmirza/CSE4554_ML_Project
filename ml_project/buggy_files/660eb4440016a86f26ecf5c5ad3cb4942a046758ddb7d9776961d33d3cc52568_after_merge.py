def get_checkbox_style(color="#B5B5B5"):
    return """QCheckBox { color: %s; }
                QCheckBox::indicator:unchecked {border: 1px solid #555;}
                """ % color