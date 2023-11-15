    def process(self, scenes, tmp_dir):
        evaluation = self.create_evaluation()
        vect_evaluation = self.create_evaluation()
        null_class_id = self.class_config.get_null_class_id()

        for scene in scenes:
            log.info('Computing evaluation for scene {}...'.format(scene.id))
            label_source = scene.ground_truth_label_source
            label_store = scene.prediction_label_store
            with ActivateMixin.compose(label_source, label_store):
                ground_truth = label_source.get_labels()
                predictions = label_store.get_labels()

                if scene.aoi_polygons:
                    # Filter labels based on AOI.
                    ground_truth = ground_truth.filter_by_aoi(
                        scene.aoi_polygons, null_class_id)
                    predictions = predictions.filter_by_aoi(
                        scene.aoi_polygons, null_class_id)
                scene_evaluation = self.create_evaluation()
                scene_evaluation.compute(ground_truth, predictions)
                evaluation.merge(scene_evaluation, scene_id=scene.id)

            if hasattr(label_source, 'raster_source') and hasattr(
                    label_source.raster_source, 'vector_source') and hasattr(
                        label_store, 'vector_output'):
                gt_geojson = label_source.raster_source.vector_source.get_geojson(
                )
                for vo in label_store.vector_output:
                    pred_geojson_uri = vo.uri
                    mode = vo.get_mode()
                    class_id = vo.class_id
                    pred_geojson_source = GeoJSONVectorSourceConfig(
                        uri=pred_geojson_uri, default_class_id=class_id).build(
                            self.class_config,
                            scene.raster_source.get_crs_transformer())
                    pred_geojson = pred_geojson_source.get_geojson()

                    if scene.aoi_polygons:
                        gt_geojson = filter_geojson_by_aoi(
                            gt_geojson, scene.aoi_polygons)
                        pred_geojson = filter_geojson_by_aoi(
                            pred_geojson, scene.aoi_polygons)

                    vect_scene_evaluation = self.create_evaluation()
                    vect_scene_evaluation.compute_vector(
                        gt_geojson, pred_geojson, mode, class_id)
                    vect_evaluation.merge(
                        vect_scene_evaluation, scene_id=scene.id)

        if not evaluation.is_empty():
            evaluation.save(self.output_uri)
        if not vect_evaluation.is_empty():
            vect_evaluation.save(self.vector_output_uri)