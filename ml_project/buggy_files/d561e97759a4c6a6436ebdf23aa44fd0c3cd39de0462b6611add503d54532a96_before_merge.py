    def __geo_interface__(self):
        coords = [tuple(self.exterior.coords)]
        for hole in self.interiors:
            coords.append(tuple(hole.coords))
        return {
            'type': 'Polygon',
            'coordinates': tuple(coords)
            }