    def break_apart_paths(self, paths):
        polygons = []
        for path in paths:
            if len(path) < 3:
                continue
            linestring = LineString(path)
            if not linestring.is_simple:
                linestring = unary_union(linestring)
                for polygon in polygonize(linestring):
                    polygons.append(polygon)
            else:
                polygon = Polygon(path).buffer(0)
                polygons.append(polygon)
        return polygons