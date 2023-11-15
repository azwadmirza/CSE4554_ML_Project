    def filter_by_aoi(self, aoi_polygons):
        boxes = self.get_boxes()
        class_ids = self.get_class_ids()
        scores = self.get_scores()

        new_boxes = []
        new_class_ids = []
        new_scores = []
        for box, class_id, score in zip(boxes, class_ids, scores):
            box_poly = box.to_shapely()
            for aoi in aoi_polygons:
                if box_poly.within(aoi):
                    new_boxes.append(box)
                    new_class_ids.append(class_id)
                    new_scores.append(score)
                    break

        return ObjectDetectionLabels(
            np.array(new_boxes), np.array(new_class_ids), np.array(new_scores))