    def get_property_file_text(self, workspace):
        """Get the text for all property files

        workspace - the workspace from prepare_run

        Returns a list of Property objects which describe each property file

        The Property object has the following attributes:

        * object_name - the name of the object: "Object" if combining all tables,
                        otherwise the name of the relevant object.

        * file_name - save text in this file

        * text - the text to save

        * properties - a key / value dictionary of the properties
        """

        class Properties(object):
            def __init__(self, object_name, file_name, text):
                self.object_name = object_name
                self.file_name = file_name
                self.text = text
                self.properties = {}
                for line in text.split("\n"):
                    line = line.strip()
                    if line.startswith("#") or line.find("=") == -1:
                        continue
                    k, v = [x.strip() for x in line.split("=", 1)]
                    self.properties[k] = v

        result = []
        #
        # Get appropriate object names
        #
        if self.objects_choice != O_NONE:
            if self.separate_object_tables == OT_COMBINE:
                object_names = [self.location_object.value]
            elif self.separate_object_tables == OT_PER_OBJECT:
                if self.objects_choice == O_SELECT:
                    object_names = self.objects_list.value.split(",")
                else:
                    object_names = [
                        object_name
                        for object_name in workspace.measurements.get_object_names()
                        if (object_name != cellprofiler_core.measurement.IMAGE)
                        and (not self.ignore_object(object_name))
                    ]
            elif self.separate_object_tables == OT_VIEW:
                object_names = [None]
        else:
            object_names = [None]

        default_image_names = []
        # Find all images that have FileName and PathName
        image_features = [
            c[1]
            for c in workspace.pipeline.get_measurement_columns()
            if c[0] == cellprofiler_core.measurement.IMAGE
        ]
        for feature in image_features:
            match = re.match(
                "^%s_(.+)$" % cellprofiler_core.measurement.C_FILE_NAME, feature
            )
            if match:
                default_image_names.append(match.groups()[0])

        if not self.properties_export_all_image_defaults:
            # Extract the user-specified images
            user_image_names = []
            for group in self.image_groups:
                user_image_names.append(group.image_cols.value)

        if self.db_type == DB_SQLITE:
            name = os.path.splitext(self.sqlite_file.value)[0]
        else:
            name = self.db_name.value
        tbl_prefix = self.get_table_prefix()
        if tbl_prefix != "":
            if tbl_prefix.endswith("_"):
                tbl_prefix = tbl_prefix[:-1]
            name = "_".join((name, tbl_prefix))

        tblname = name
        date = datetime.datetime.now().ctime()
        db_type = (
            (self.db_type == DB_MYSQL and "mysql")
            or (self.db_type == DB_SQLITE and "sqlite")
            or "oracle_not_supported"
        )
        db_port = (
            (self.db_type == DB_MYSQL and 3306)
            or (self.db_type == DB_ORACLE and 1521)
            or ""
        )
        db_host = self.db_host
        db_pwd = self.db_passwd
        db_name = self.db_name
        db_user = self.db_user
        db_sqlite_file = (
            self.db_type == DB_SQLITE
            and self.make_full_filename(self.sqlite_file.value)
        ) or ""
        if self.db_type == DB_MYSQL or self.db_type == DB_ORACLE:
            db_info = "db_type      = %(db_type)s\n" % (locals())
            db_info += "db_port      = %(db_port)d\n" % (locals())
            db_info += "db_host      = %(db_host)s\n" % (locals())
            db_info += "db_name      = %(db_name)s\n" % (locals())
            db_info += "db_user      = %(db_user)s\n" % (locals())
            db_info += "db_passwd    = %(db_pwd)s" % (locals())
        elif self.db_type == DB_SQLITE:
            db_info = "db_type         = %(db_type)s\n" % (locals())
            db_info += "db_sqlite_file  = %(db_sqlite_file)s" % (locals())
        elif self.db_type == DB_MYSQL_CSV:
            db_info = "db_type      = mysql\n"
            db_info += "db_port      = \n"
            db_info += "db_host      = \n"
            db_info += "db_name      = %(db_name)s\n" % (locals())
            db_info += "db_user      = \n"
            db_info += "db_passwd    = "

        spot_tables = "%sPer_Image" % (self.get_table_prefix())
        classification_type = (
            "image" if self.properties_classification_type.value == CT_IMAGE else ""
        )

        for object_name in object_names:
            if object_name:
                if self.objects_choice != O_NONE:
                    if self.separate_object_tables == OT_COMBINE:
                        cell_tables = "%sPer_Object" % (self.get_table_prefix())
                        object_id = C_OBJECT_NUMBER
                        filename = "%s.properties" % tblname
                        properties_object_name = "Object"
                        object_count = "Image_Count_%s" % self.location_object.value
                        cell_x_loc = "%s_Location_Center_X" % self.location_object.value
                        cell_y_loc = "%s_Location_Center_Y" % self.location_object.value
                    elif self.separate_object_tables == OT_PER_OBJECT:
                        cell_tables = "%sPer_%s" % (
                            self.get_table_prefix(),
                            object_name,
                        )
                        object_id = "%s_Number_Object_Number" % object_name
                        filename = "%s_%s.properties" % (tblname, object_name)
                        properties_object_name = object_name
                        object_count = "Image_Count_%s" % object_name
                        cell_x_loc = "%s_Location_Center_X" % object_name
                        cell_y_loc = "%s_Location_Center_Y" % object_name
            else:
                """If object_name = None, it's either per_image only or a view """
                if self.objects_choice == O_NONE:
                    cell_tables = ""
                    object_id = ""
                    filename = "%s.properties" % tblname
                    properties_object_name = object_name
                    object_count = ""
                    cell_x_loc = ""
                    cell_y_loc = ""
                elif self.separate_object_tables == OT_VIEW:
                    cell_tables = "%sPer_Object" % (self.get_table_prefix())
                    object_id = C_OBJECT_NUMBER
                    filename = "%s.properties" % tblname
                    properties_object_name = "Object"
                    object_count = "Image_Count_%s" % self.location_object.value
                    cell_x_loc = "%s_Location_Center_X" % self.location_object.value
                    cell_y_loc = "%s_Location_Center_Y" % self.location_object.value

            file_name = self.make_full_filename(filename, workspace)
            unique_id = C_IMAGE_NUMBER
            image_thumbnail_cols = (
                ",".join(
                    [
                        "%s_%s_%s"
                        % (cellprofiler_core.measurement.IMAGE, C_THUMBNAIL, name)
                        for name in self.thumbnail_image_names.get_selections()
                    ]
                )
                if self.want_image_thumbnails
                else ""
            )

            if self.properties_export_all_image_defaults:
                image_file_cols = ",".join(
                    [
                        "%s_%s_%s"
                        % (
                            cellprofiler_core.measurement.IMAGE,
                            cellprofiler_core.measurement.C_FILE_NAME,
                            name,
                        )
                        for name in default_image_names
                    ]
                )
                image_path_cols = ",".join(
                    [
                        "%s_%s_%s"
                        % (
                            cellprofiler_core.measurement.IMAGE,
                            cellprofiler_core.measurement.C_PATH_NAME,
                            name,
                        )
                        for name in default_image_names
                    ]
                )

                # Provide default colors
                if len(default_image_names) == 1:
                    image_channel_colors = "gray,"
                else:
                    image_channel_colors = (
                        "red, green, blue, cyan, magenta, yellow, gray, "
                        + ("none, " * 10)
                    )
                    num_images = (
                        len(default_image_names)
                        + len(
                            set(
                                [
                                    name
                                    for name in self.thumbnail_image_names.get_selections()
                                ]
                            ).difference(default_image_names)
                        )
                        if self.want_image_thumbnails
                        else 0
                    )
                    image_channel_colors = ",".join(
                        image_channel_colors.split(",")[:num_images]
                    )
                image_names_csl = ",".join(
                    default_image_names
                )  # Convert to comma-separated list

                if self.want_image_thumbnails:
                    selected_thumbs = [
                        name for name in self.thumbnail_image_names.get_selections()
                    ]
                    thumb_names = [
                        name for name in default_image_names if name in selected_thumbs
                    ] + [
                        name
                        for name in selected_thumbs
                        if name not in default_image_names
                    ]
                    image_thumbnail_cols = ",".join(
                        [
                            "%s_%s_%s"
                            % (cellprofiler_core.measurement.IMAGE, C_THUMBNAIL, name)
                            for name in thumb_names
                        ]
                    )
                else:
                    image_thumbnail_cols = ""

            else:
                # Extract user-specified image names and colors
                user_image_names = []
                image_channel_colors = []
                selected_image_names = []
                for group in self.image_groups:
                    selected_image_names += [group.image_cols.value]
                    if group.wants_automatic_image_name:
                        user_image_names += [group.image_cols.value]
                    else:
                        user_image_names += [group.image_name.value]
                    image_channel_colors += [group.image_channel_colors.value]

                image_file_cols = ",".join(
                    [
                        "%s_%s_%s"
                        % (
                            cellprofiler_core.measurement.IMAGE,
                            cellprofiler_core.measurement.C_FILE_NAME,
                            name,
                        )
                        for name in selected_image_names
                    ]
                )
                image_path_cols = ",".join(
                    [
                        "%s_%s_%s"
                        % (
                            cellprofiler_core.measurement.IMAGE,
                            cellprofiler_core.measurement.C_PATH_NAME,
                            name,
                        )
                        for name in selected_image_names
                    ]
                )

                # Try to match thumbnail order to selected image order
                if self.want_image_thumbnails:
                    selected_thumbs = [
                        name for name in self.thumbnail_image_names.get_selections()
                    ]
                    thumb_names = [
                        name for name in selected_image_names if name in selected_thumbs
                    ] + [
                        name
                        for name in selected_thumbs
                        if name not in selected_image_names
                    ]
                    image_thumbnail_cols = ",".join(
                        [
                            "%s_%s_%s"
                            % (cellprofiler_core.measurement.IMAGE, C_THUMBNAIL, name)
                            for name in thumb_names
                        ]
                    )
                else:
                    image_thumbnail_cols = ""
                    selected_thumbs = []

                # Convert to comma-separated list
                image_channel_colors = ",".join(
                    image_channel_colors
                    + ["none"]
                    * len(set(selected_thumbs).difference(selected_image_names))
                )
                image_names_csl = ",".join(user_image_names)

            group_statements = ""
            if self.properties_wants_groups:
                for group in self.group_field_groups:
                    group_statements += (
                        "group_SQL_"
                        + group.group_name.value
                        + " = SELECT "
                        + group.group_statement.value
                        + " FROM "
                        + spot_tables
                        + "\n"
                    )

            filter_statements = ""
            if self.properties_wants_filters:
                if self.create_filters_for_plates:
                    plate_key = self.properties_plate_metadata.value
                    metadata_groups = workspace.measurements.group_by_metadata(
                        [plate_key]
                    )
                    for metadata_group in metadata_groups:
                        plate_text = re.sub(
                            "[^A-Za-z0-9_]", "_", metadata_group.get(plate_key)
                        )  # Replace any odd characters with underscores
                        filter_name = "Plate_%s" % plate_text
                        filter_statements += (
                            "filter_SQL_" + filter_name + " = SELECT ImageNumber"
                            " FROM " + spot_tables + " WHERE Image_Metadata_%s"
                            ' = "%s"\n' % (plate_key, metadata_group.get(plate_key))
                        )

                for group in self.filter_field_groups:
                    filter_statements += (
                        "filter_SQL_"
                        + group.filter_name.value
                        + " = SELECT ImageNumber"
                        " FROM "
                        + spot_tables
                        + " WHERE "
                        + group.filter_statement.value
                        + "\n"
                    )

            image_url = (
                self.properties_image_url_prepend.value
                if self.wants_properties_image_url_prepend
                else ""
            )
            plate_type = (
                ""
                if self.properties_plate_type.value == NONE_CHOICE
                else self.properties_plate_type.value
            )
            plate_id = (
                ""
                if self.properties_plate_metadata.value == NONE_CHOICE
                else "%s_%s_%s"
                % (
                    cellprofiler_core.measurement.IMAGE,
                    cellprofiler_core.measurement.C_METADATA,
                    self.properties_plate_metadata.value,
                )
            )
            well_id = (
                ""
                if self.properties_well_metadata.value == NONE_CHOICE
                else "%s_%s_%s"
                % (
                    cellprofiler_core.measurement.IMAGE,
                    cellprofiler_core.measurement.C_METADATA,
                    self.properties_well_metadata.value,
                )
            )
            class_table = (
                self.get_table_prefix() + self.properties_class_table_name.value
            )

            contents = """#%(date)s
# ==============================================
#
# CellProfiler Analyst 2.0 properties file
#
# ==============================================

# ==== Database Info ====
%(db_info)s

# ==== Database Tables ====
image_table   = %(spot_tables)s
object_table  = %(cell_tables)s

# ==== Database Columns ====
# Specify the database column names that contain unique IDs for images and
# objects (and optionally tables).
#
# table_id (OPTIONAL): This field lets Classifier handle multiple tables if
#          you merge them into one and add a table_number column as a foreign
#          key to your per-image and per-object tables.
# image_id: must be a foreign key column between your per-image and per-object
#           tables
# object_id: the object key column from your per-object table

image_id      = %(unique_id)s
object_id     = %(object_id)s
plate_id      = %(plate_id)s
well_id       = %(well_id)s
series_id     = Image_Group_Number
group_id      = Image_Group_Number
timepoint_id  = Image_Group_Index

# Also specify the column names that contain X and Y coordinates for each
# object within an image.
cell_x_loc    = %(cell_x_loc)s
cell_y_loc    = %(cell_y_loc)s

# ==== Image Path and File Name Columns ====
# Classifier needs to know where to find the images from your experiment.
# Specify the column names from your per-image table that contain the image
# paths and file names here.
#
# Individual image files are expected to be monochromatic and represent a single
# channel. However, any number of images may be combined by adding a new channel
# path and filename column to the per-image table of your database and then
# adding those column names here.
#
# Note that these lists must have equal length!
image_path_cols = %(image_path_cols)s
image_file_cols = %(image_file_cols)s

# CellProfiler Analyst will now read image thumbnails directly from the database, if chosen in ExportToDatabase.
image_thumbnail_cols = %(image_thumbnail_cols)s

# Give short names for each of the channels (respectively)...
image_names = %(image_names_csl)s

# Specify a default color for each of the channels (respectively)
# Valid colors are: [red, green, blue, magenta, cyan, yellow, gray, none]
image_channel_colors = %(image_channel_colors)s

# ==== Image Accesss Info ====
image_url_prepend = %(image_url)s

# ==== Dynamic Groups ====
# Here you can define groupings to choose from when classifier scores your experiment.  (e.g., per-well)
# This is OPTIONAL, you may leave "groups = ".
# FORMAT:
#   group_XXX  =  MySQL select statement that returns image-keys and group-keys.  This will be associated with the group name "XXX" from above.
# EXAMPLE GROUPS:
#   groups               =  Well, Gene, Well+Gene,
#   group_SQL_Well       =  SELECT Per_Image_Table.TableNumber, Per_Image_Table.ImageNumber, Per_Image_Table.well FROM Per_Image_Table
#   group_SQL_Gene       =  SELECT Per_Image_Table.TableNumber, Per_Image_Table.ImageNumber, Well_ID_Table.gene FROM Per_Image_Table, Well_ID_Table WHERE Per_Image_Table.well=Well_ID_Table.well
#   group_SQL_Well+Gene  =  SELECT Per_Image_Table.TableNumber, Per_Image_Table.ImageNumber, Well_ID_Table.well, Well_ID_Table.gene FROM Per_Image_Table, Well_ID_Table WHERE Per_Image_Table.well=Well_ID_Table.well

%(group_statements)s

# ==== Image Filters ====
# Here you can define image filters to let you select objects from a subset of your experiment when training the classifier.
# FORMAT:
#   filter_SQL_XXX  =  MySQL select statement that returns image keys you wish to filter out.  This will be associated with the filter name "XXX" from above.
# EXAMPLE FILTERS:
#   filters           =  EMPTY, CDKs,
#   filter_SQL_EMPTY  =  SELECT TableNumber, ImageNumber FROM CPA_per_image, Well_ID_Table WHERE CPA_per_image.well=Well_ID_Table.well AND Well_ID_Table.Gene="EMPTY"
#   filter_SQL_CDKs   =  SELECT TableNumber, ImageNumber FROM CPA_per_image, Well_ID_Table WHERE CPA_per_image.well=Well_ID_Table.well AND Well_ID_Table.Gene REGEXP 'CDK.*'

%(filter_statements)s

# ==== Meta data ====
# What are your objects called?
# FORMAT:
#   object_name  =  singular object name, plural object name,
object_name  =  cell, cells,

# What size plates were used?  96, 384 or 5600?  This is for use in the PlateViewer. Leave blank if none
plate_type  = %(plate_type)s

# ==== Excluded Columns ====
# OPTIONAL
# Classifier uses columns in your per_object table to find rules. It will
# automatically ignore ID columns defined in table_id, image_id, and object_id
# as well as any columns that contain non-numeric data.
#
# Here you may list other columns in your per_object table that you wish the
# classifier to ignore when finding rules.
#
# You may also use regular expressions here to match more general column names.
#
# Example: classifier_ignore_columns = WellID, Meta_.*, .*_Position
#   This will ignore any column named "WellID", any columns that start with
#   "Meta_", and any columns that end in "_Position".
#
# A more restrictive example:
# classifier_ignore_columns = ImageNumber, ObjectNumber, .*Parent.*, .*Children.*, .*_Location_Center_.*,.*_Metadata_.*

classifier_ignore_columns  =  table_number_key_column, image_number_key_column, object_number_key_column

# ==== Other ====
# Specify the approximate diameter of your objects in pixels here.
image_tile_size   =  50

# Provides the image width and height. Used for per-image classification.
# If not set, it will be obtained from the Image_Width and Image_Height
# measurements in CellProfiler.

# image_width  = 1000
# image_height = 1000

# OPTIONAL
# Image Gallery can use a different tile size (in pixels) to create thumbnails for images
# If not set, it will be the same as image_tile_size

image_size =

# ======== Classification type ========
# OPTIONAL
# CPA 2.2.0 allows image classification instead of object classification.
# If left blank or set to "object", then Classifier will fetch objects (default).
# If set to "image", then Classifier will fetch whole images instead of objects.

classification_type  = %(classification_type)s

# ======== Auto Load Training Set ========
# OPTIONAL
# You may enter the full path to a training set that you would like Classifier
# to automatically load when started.

training_set  =

# ======== Area Based Scoring ========
# OPTIONAL
# You may specify a column in your per-object table which will be summed and
# reported in place of object-counts when scoring.  The typical use for this
# is to report the areas of objects on a per-image or per-group basis.

area_scoring_column =

# ======== Output Per-Object Classes ========
# OPTIONAL
# Here you can specify a MySQL table in your Database where you would like
# Classifier to write out class information for each object in the
# object_table

class_table  = %(class_table)s

# ======== Check Tables ========
# OPTIONAL
# [yes/no]  You can ask classifier to check your tables for anomalies such
# as orphaned objects or missing column indices.  Default is on.
# This check is run when Classifier starts and may take up to a minute if
# your object_table is extremely large.

check_tables = yes
    """ % (
                locals()
            )
            result.append(Properties(properties_object_name, file_name, contents))
        return result