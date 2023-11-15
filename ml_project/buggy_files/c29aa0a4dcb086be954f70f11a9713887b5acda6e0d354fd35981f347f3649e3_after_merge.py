    def _slice_area_from_bbox(self, src_area, dst_area, ll_bbox=None,
                              xy_bbox=None):
        """Slice the provided area using the bounds provided."""
        if ll_bbox is not None:
            dst_area = AreaDefinition(
                'crop_area', 'crop_area', 'crop_latlong',
                {'proj': 'latlong'}, 100, 100, ll_bbox)
        elif xy_bbox is not None:
            crs = src_area.crs if hasattr(src_area, 'crs') else src_area.proj_dict
            dst_area = AreaDefinition(
                'crop_area', 'crop_area', 'crop_xy',
                crs, src_area.x_size, src_area.y_size,
                xy_bbox)
        x_slice, y_slice = src_area.get_area_slices(dst_area)
        return src_area[y_slice, x_slice], y_slice, x_slice