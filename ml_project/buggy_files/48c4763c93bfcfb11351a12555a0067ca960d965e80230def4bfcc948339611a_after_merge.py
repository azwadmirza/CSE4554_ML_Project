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
                #
                # Find the module that provides the image we need
                #
                md = workspace.pipeline.get_provider_dictionary(
                    self.image_name.group, self)
                src_module, src_setting = md[self.image_name.value][-1]
                modules = list(pipeline.modules())
                idx = modules.index(src_module)
                last_module = modules[idx+1]
                for w in pipeline.run_group_with_yield(
                    workspace, grouping, image_numbers, 
                    last_module, title, message):
                    image = w.image_set.get_image(self.image_name.value,
                                                  cache = False)
                    output_image_provider.add_image(image)
                    w.image_set.clear_cache()
            output_image_provider.serialize(d)
            
        return True