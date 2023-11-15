    def to_py(self, value: _StrUnset) -> typing.Union[usertypes.Unset,
                                                      None, QFont]:
        self._basic_py_validation(value, str)
        if isinstance(value, usertypes.Unset):
            return value
        elif not value:
            return None

        font = QFont()
        font.setStyle(QFont.StyleNormal)
        font.setWeight(QFont.Normal)

        match = self.font_regex.fullmatch(value)
        if not match:  # pragma: no cover
            # This should never happen, as the regex always matches everything
            # as family.
            raise configexc.ValidationError(value, "must be a valid font")

        style = match.group('style')
        weight = match.group('weight')
        namedweight = match.group('namedweight')
        size = match.group('size')
        family_str = match.group('family')

        style_map = {
            'normal': QFont.StyleNormal,
            'italic': QFont.StyleItalic,
            'oblique': QFont.StyleOblique,
        }
        if style:
            font.setStyle(style_map[style])

        weight_map = {
            'normal': QFont.Normal,
            'bold': QFont.Bold,
        }
        if namedweight:
            font.setWeight(weight_map[namedweight])
        elif weight:
            # based on qcssparser.cpp:setFontWeightFromValue
            font.setWeight(min(int(weight) // 8, 99))

        if size:
            if size == 'default_size':
                size = self.default_size

            if size.lower().endswith('pt'):
                font.setPointSizeF(float(size[:-2]))
            elif size.lower().endswith('px'):
                font.setPixelSize(int(size[:-2]))
            else:
                # This should never happen as the regex only lets pt/px
                # through.
                raise ValueError("Unexpected size unit in {!r}!".format(
                    size))  # pragma: no cover

        families = self._parse_families(family_str)
        if hasattr(font, 'setFamilies'):
            # Added in Qt 5.13
            font.setFamily(families.family)  # type: ignore
            font.setFamilies(list(families))
        else:  # pragma: no cover
            font.setFamily(families.to_str(quote=False))

        return font