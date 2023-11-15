    def get_measurement_columns(self, pipeline):
        '''Return information on the measurements made during cropping'''
        return [(cpmeas.IMAGE,
                 x % self.cropped_image_name.value,
                 cpmeas.COLTYPE_INTEGER)
                for x in (FF_AREA_RETAINED, FF_ORIGINAL_AREA)]