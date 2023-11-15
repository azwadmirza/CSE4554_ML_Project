    def effect(self):  # noqa: C901
        if not self.selected:
            inkex.errormsg(_("Please select one or more fill areas to break apart."))
            return

        elements = []
        nodes = self.get_nodes()
        for node in nodes:
            if node.tag in SVG_PATH_TAG:
                elements.append(EmbroideryElement(node))

        for element in elements:
            if not element.get_style("fill", "black"):
                continue

            # we don't want to touch valid elements
            paths = element.flatten(element.parse_path())
            try:
                paths.sort(key=lambda point_list: Polygon(point_list).area, reverse=True)
                polygon = MultiPolygon([(paths[0], paths[1:])])
                if self.geom_is_valid(polygon):
                    continue
            except ValueError:
                pass

            polygons = self.break_apart_paths(paths)
            polygons = self.ensure_minimum_size(polygons, 5)
            if self.options.method == 1:
                polygons = self.combine_overlapping_polygons(polygons)
            polygons = self.recombine_polygons(polygons)
            if polygons:
                self.polygons_to_nodes(polygons, element)