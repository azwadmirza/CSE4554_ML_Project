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
        current_position = 0.0
        for i in range(len(coords)-1):
            point1 = coords[i]
            point2 = coords[i+1]
            dx = point1[0] - point2[0]
            dy = point1[1] - point2[1]
            segment_length = (dx ** 2 + dy ** 2) ** 0.5
            current_position += segment_length
            if distance_on_line == current_position:
                # splitter is exactly on a vertex
                return [
                    LineString(coords[:i+2]),
                    LineString(coords[i+1:])
                ]
            elif distance_on_line < current_position:
                # splitter is between two vertices
                return [
                    LineString(coords[:i+1] + [splitter.coords[0]]),
                    LineString([splitter.coords[0]] + coords[i+1:])
                ]
        return [line]