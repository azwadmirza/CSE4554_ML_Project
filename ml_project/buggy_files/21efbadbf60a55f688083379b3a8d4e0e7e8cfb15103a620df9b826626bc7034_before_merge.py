    def break_apart_paths(self, paths):
        polygons = []
        for path in paths:
            linestring = LineString(path)
            polygon = Polygon(path).buffer(0)
            if not linestring.is_simple:
                linestring = unary_union(linestring)
                for polygon in polygonize(linestring):
                    polygons.append(polygon)
            else:
                polygons.append(polygon)
        return polygons