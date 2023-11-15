    def validate(self, color, against=None, enforce=None):
        # If not checking against anything, check against everything
        if not against:
            against = list(colorSpaces)
        # If looking for a string, convert from other forms it could be in
        if enforce == str:
            color = str(color).lower()
        # If looking for a tuple, convert from other forms it could be in
        if enforce == tuple or enforce == (tuple, int):
            if isinstance(color, str):
                color = [float(n) for n in color.strip('[]()').split(',')]
            if isinstance(color, list):
                color = tuple(color)

        # If enforcing multiple
        if enforce == (tuple, int):
            alpha = (color[-1],) if len(color) == 4 else ()
            color = tuple(int(round(c)) for c in color[:3]) + alpha
        # Get possible colour spaces
        possible = Color.getSpace(color)
        if isinstance(possible, str):
            possible = [possible]
        # Return if any matches
        for space in possible:
            if space in against:
                return color
        # If no matches...
        self.named = None
        return None