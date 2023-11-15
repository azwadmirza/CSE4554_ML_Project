    def prepare_group(self, workspace, grouping, image_numbers):
        image_set_list = workspace.image_set_list
        pipeline = workspace.pipeline
        assert isinstance(pipeline, cpp.Pipeline)
        m = workspace.measurements
        assert isinstance(m, cpmeas.Measurements)
        if self.each_or_all != EA_EACH and len(image_numbers) > 0:
            title = "#%d: CorrectIlluminationCalculate for %s"%(
                self.module_num, self.image_name)
            message = ("CorrectIlluminationCalculate is averaging %d images while "
                       "preparing for run"%(len(image_numbers)))
            output_image_provider = CorrectIlluminationImageProvider(
                self.illumination_image_name.value, self)
            d = self.get_dictionary(image_set_list)[OUTPUT_IMAGE] = {}
            if self.each_or_all == EA_ALL_FIRST:
                for w in pipeline.run_group_with_yield(
                    workspace, grouping, image_numbers, self, title, message):
                    image = w.image_set.get_image(self.image_name.value,
                                                  cache = False)
                    output_image_provider.add_image(image)
            output_image_provider.serialize(d)
            
        return True