    def export_annotations(self,export_range,export_dir):

        if not self.annotations:
            logger.warning('No annotations in this recording nothing to export')
            return

        annotations_in_section = chain(*self.annotations_by_frame[export_range])
        annotations_in_section = { a['index']:a for a in annotations_in_section}.values() #remove dublicates
        annotations_in_section.sort(key=lambda a:a['index'])

        with open(os.path.join(export_dir,'annotations.csv'),'w',encoding='utf-8',newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(self.csv_representation_keys())
            for a in annotations_in_section:
                csv_writer.writerow(self.csv_representation_for_annotations(a))
            logger.info("Created 'annotations.csv' file.")