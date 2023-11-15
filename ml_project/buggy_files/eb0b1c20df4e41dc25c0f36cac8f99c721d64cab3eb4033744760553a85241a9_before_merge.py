    def _parse_token(self, token, value, parts):

        if token == "YYYY":
            parts["year"] = int(value)

        elif token == "YY":
            value = int(value)
            parts["year"] = 1900 + value if value > 68 else 2000 + value

        elif token in ["MMMM", "MMM"]:
            parts["month"] = self.locale.month_number(value.lower())

        elif token in ["MM", "M"]:
            parts["month"] = int(value)

        elif token in ["DDDD", "DDD"]:
            parts["day_of_year"] = int(value)

        elif token in ["DD", "D"]:
            parts["day"] = int(value)

        elif token == "Do":
            parts["day"] = int(value)

        elif token == "dddd":
            parts["day_of_week"] = self.locale.day_names.index(value) - 1

        elif token == "ddd":
            parts["day_of_week"] = self.locale.day_abbreviations.index(value) - 1

        elif token.upper() in ["HH", "H"]:
            parts["hour"] = int(value)

        elif token in ["mm", "m"]:
            parts["minute"] = int(value)

        elif token in ["ss", "s"]:
            parts["second"] = int(value)

        elif token == "S":
            # We have the *most significant* digits of an arbitrary-precision integer.
            # We want the six most significant digits as an integer, rounded.
            # IDEA: add nanosecond support somehow? Need datetime support for it first.
            value = value.ljust(7, str("0"))

            # floating-point (IEEE-754) defaults to half-to-even rounding
            seventh_digit = int(value[6])
            if seventh_digit == 5:
                rounding = int(value[5]) % 2
            elif seventh_digit > 5:
                rounding = 1
            else:
                rounding = 0

            parts["microsecond"] = int(value[:6]) + rounding

        elif token == "X":
            parts["timestamp"] = float(value)

        elif token == "x":
            parts["expanded_timestamp"] = int(value)

        elif token in ["ZZZ", "ZZ", "Z"]:
            parts["tzinfo"] = TzinfoParser.parse(value)

        elif token in ["a", "A"]:
            if value in (self.locale.meridians["am"], self.locale.meridians["AM"]):
                parts["am_pm"] = "am"
            elif value in (self.locale.meridians["pm"], self.locale.meridians["PM"]):
                parts["am_pm"] = "pm"

        elif token == "W":
            parts["weekdate"] = value