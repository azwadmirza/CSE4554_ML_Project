    def _parse_image(self, xml_node, overview=False):
        """parse image from bruker xml image node."""
        if overview:
            rect_node = xml_node.find("./ChildClassInstances"
                "/ClassInstance["
                #"@Type='TRTRectangleOverlayElement' and "
                "@Name='Map']/TRTSolidOverlayElement/"
                "TRTBasicLineOverlayElement/TRTOverlayElement")
            over_rect = dictionarize(rect_node)['TRTOverlayElement']['Rect']
            rect = {'y1': over_rect['Top'] * self.y_res,
                    'x1': over_rect['Left'] * self.x_res,
                    'y2': over_rect['Bottom'] * self.y_res,
                    'x2': over_rect['Right'] * self.x_res}
            over_dict = {'marker_type': 'Rectangle',
                         'plot_on_signal': True,
                         'data': rect,
                         'marker_properties': {'color': 'yellow',
                                               'linewidth': 2}}
        image = Container()
        image.width = int(xml_node.find('./Width').text)  # in pixels
        image.height = int(xml_node.find('./Height').text)  # in pixels
        image.plane_count = int(xml_node.find('./PlaneCount').text)
        image.images = []
        for i in range(image.plane_count):
            img = xml_node.find("./Plane" + str(i))
            raw = codecs.decode((img.find('./Data').text).encode('ascii'),'base64')
            array1 = np.frombuffer(raw, dtype=np.uint16)
            if any(array1):
                item = self.gen_hspy_item_dict_basic()
                data = array1.reshape((image.height, image.width))
                detector_name = str(img.find('./Description').text)
                item['data'] = data
                item['axes'][0]['size'] = image.height
                item['axes'][1]['size'] = image.width
                item['metadata']['General'] = {'title': detector_name}
                item['metadata']['Signal'] = {'signal_type': detector_name,
                                              'record_by': 'image'}
                if overview:
                    item['metadata']['Markers'] = {'overview': over_dict}
                image.images.append(item)
        return image