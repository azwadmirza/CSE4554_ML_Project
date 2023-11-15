    def get_measurement_columns(self, pipeline):
        """Return information on the measurements made during cropping"""
        return [(cellprofiler.measurement.IMAGE,
                 x % self.cropped_image_name.value,
                 cellprofiler.measurement.COLTYPE_INTEGER)
                for x in (FF_AREA_RETAINED, FF_ORIGINAL_AREA)]