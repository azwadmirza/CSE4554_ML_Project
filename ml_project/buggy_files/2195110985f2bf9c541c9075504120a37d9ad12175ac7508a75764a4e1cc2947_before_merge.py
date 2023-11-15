    def _split_line_with_point(line, splitter):
        """Split a LineString with a Point"""

        assert(isinstance(line, LineString))
        assert(isinstance(splitter, Point))

        # check if point is in the interior of the line
        if not line.relate_pattern(splitter, '0********'):
            # point not on line interior --> return collection with single identity line
            # (REASONING: Returning a list with the input line reference and creating a
            # GeometryCollection at the general split function prevents unnecessary copying
            # of linestrings in multipoint splitting function)
            return [line]
        elif line.coords[0] == splitter.coords[0]:
            # if line is a closed ring the previous test doesn't behave as desired
            return [line]

        # point is on line, get the distance from the first point on line
        distance_on_line = line.project(splitter)
        coords = list(line.coords)
        # split the line at the point and create two new lines
        # TODO: can optimize this by accumulating the computed point-to-point distances
        for i, p in enumerate(coords):
            pd = line.project(Point(p))
            if pd == distance_on_line:
                return [
                    LineString(coords[:i+1]),
                    LineString(coords[i:])
                ]
            elif distance_on_line < pd:
                # we must interpolate here because the line might use 3D points
                cp = line.interpolate(distance_on_line)
                ls1_coords = coords[:i]
                ls1_coords.append(cp.coords[0])
                ls2_coords = [cp.coords[0]]
                ls2_coords.extend(coords[i:])
                return [LineString(ls1_coords), LineString(ls2_coords)]