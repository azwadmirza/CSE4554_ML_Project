    def create_settings(self):
        super(RelateObjects, self).create_settings()

        self.x_name.text = "Parent objects"

        self.x_name.doc = """
        Parent objects are defined as those objects which encompass the child object.
        For example, when relating speckles to the nuclei that contains them, the nuclei are the parents.
        """

        self.y_name = cellprofiler.setting.ObjectNameSubscriber(
            "Child objects",
            doc="""
            Child objects are defined as those objects contained within the parent object. For example, when relating
            speckles to the nuclei that contains them, the speckles are the children.
            """
        )

        self.find_parent_child_distances = cellprofiler.setting.Choice(
            "Calculate child-parent distances?",
            D_ALL,
            doc="""
            Choose the method to calculate distances of each child to its parent.
            <ul>
                <li><i>{D_NONE}:</i> Do not calculate any distances.</li>
                <li><i>{D_MINIMUM}:</i> The distance from the centroid of the child object to the closest
                perimeter point on the parent object.</li>
                <li><i>{D_CENTROID}:</i> The distance from the centroid of the child object to the centroid of
                the parent.</li>
                <li><i>{D_BOTH}:</i> Calculate both the <i>{D_MINIMUM}</i> and <i>{D_CENTROID}</i>
                distances.</li>
            </ul>
            """.format(**{
                "D_NONE": D_NONE,
                "D_MINIMUM": D_MINIMUM,
                "D_CENTROID": D_CENTROID,
                "D_BOTH": D_BOTH
            })
        )

        self.wants_step_parent_distances = cellprofiler.setting.Binary(
            "Calculate distances to other parents?",
            False,
            doc="""
            <i>(Used only if calculating distances)</i><br>
            Select <i>{YES}</i> to calculate the distances of the child objects to some other objects. These
            objects must be either parents or children of your parent object in order for this module to
            determine the distances. For instance, you might find "Nuclei" using <b>IdentifyPrimaryObjects</b>,
            find "Cells" using <b>IdentifySecondaryObjects</b> and find "Cytoplasm" using
            <b>IdentifyTertiaryObjects</b>. You can use <b>Relate</b> to relate speckles to cells and then
            measure distances to nuclei and cytoplasm. You could not use <b>RelateObjects</b> to relate
            speckles to cytoplasm and then measure distances to nuclei, because nuclei is neither a direct
            parent or child of cytoplasm.
            """.format(**{
                "YES": cellprofiler.setting.YES
            })
        )

        self.step_parent_names = []

        self.add_step_parent(can_delete=False)

        self.add_step_parent_button = cellprofiler.setting.DoSomething(
            "",
            "Add another parent",
            self.add_step_parent
        )

        self.wants_per_parent_means = cellprofiler.setting.Binary(
            "Calculate per-parent means for all child measurements?",
            False,
            doc="""
            Select <i>{YES}</i> to calculate the per-parent mean values of every upstream measurement made with
            the children objects and stores them as a measurement for the parent; the nomenclature of this new
            measurements is "Mean_&lt;child&gt;_&lt;category&gt;_&lt;feature&gt;". For this reason, this module
            should be placed <i>after</i> all <b>Measure</b> modules that make measurements of the children
            objects.
            """.format(**{
                "YES": cellprofiler.setting.YES
            })
        )