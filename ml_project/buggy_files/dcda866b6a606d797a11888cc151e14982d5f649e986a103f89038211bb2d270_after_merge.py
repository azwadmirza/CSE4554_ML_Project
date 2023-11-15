    def create_settings(self):
        db_choices = (
            [DB_SQLITE, DB_MYSQL]
            if HAS_MYSQL_DB
            else [DB_SQLITE]
        )
        self.db_type = cellprofiler_core.setting.Choice(
            "Database type",
            db_choices,
            DB_SQLITE,
            doc="""\
Specify the type of database you want to use:

-  *{DB_SQLITE}:* Writes SQLite files directly. SQLite is simpler to
   set up than MySQL and can more readily be run on your local computer
   rather than requiring a database server. More information about
   SQLite can be found `here`_.
   
-  *{DB_MYSQL}:* Writes the data directly to a MySQL database. MySQL
   is open-source software; you may require help from your local
   Information Technology group to set up a database server.

|image0|  If running this module on a computing cluster, there are a few
considerations to note:

-  The *{DB_MYSQL}* option is well-suited for cluster use, since
   multiple jobs can write to the database simultaneously.
-  The *{DB_SQLITE}* option is not as appropriate; a SQLite database
   only allows access by one job at a time.

.. _here: http://www.sqlite.org/

.. |image0| image:: {TECH_NOTE_ICON}
                """.format(
                **{
                    "TECH_NOTE_ICON": _help.TECH_NOTE_ICON,
                    "DB_MYSQL": DB_MYSQL,
                    "DB_SQLITE": DB_SQLITE,
                }
            ),
        )

        self.test_connection_button = cellprofiler_core.setting.DoSomething(
            "Test the database connection",
            "Test connection",
            self.test_connection,
            doc="""\
This button test the connection to MySQL server specified using
the settings entered by the user.""",
        )

        self.db_name = cellprofiler_core.setting.Text(
            "Database name",
            "DefaultDB",
            doc="""Select a name for the database you want to use.""",
        )

        self.experiment_name = cellprofiler_core.setting.Text(
            "Experiment name",
            "MyExpt",
            doc="""\
Select a name for the experiment. This name will be registered in the
database and linked to the tables that **ExportToDatabase** creates. You
will be able to select the experiment by name in CellProfiler Analyst
and will be able to find the experiment’s tables through database
queries.""",
        )

        self.want_table_prefix = cellprofiler_core.setting.Binary(
            "Add a prefix to table names?",
            True,
            doc="""\
Select whether you want to add a prefix to your table names. The default
table names are *Per\_Image* for the per-image table and *Per\_Object*
for the per-object table. Adding a prefix can be useful for bookkeeping
purposes.

-  Select "*{YES}*" to add a user-specified prefix to the default table
   names. If you want to distinguish multiple sets of data written to
   the same database, you probably want to use a prefix.
-  Select "*{NO}*" to use the default table names. For a one-time export
   of data, this option is fine.

Whether you chose to use a prefix or not, CellProfiler will warn you if
your choice entails overwriting an existing table.
""".format(
                **{"YES": "Yes", "NO": "No"}
            ),
        )

        self.table_prefix = cellprofiler_core.setting.Text(
            "Table prefix",
            "MyExpt_",
            doc="""\
*(Used if "Add a prefix to table names?" is selected)*

Enter the table prefix you want to use.

MySQL has a 64 character limit on the full name of the table. If the
combination of the table name and prefix exceeds this limit, you will
receive an error associated with this setting.""",
        )

        self.directory = cellprofiler_core.setting.DirectoryPath(
            "Output file location",
            dir_choices=[
                cellprofiler_core.preferences.DEFAULT_OUTPUT_FOLDER_NAME,
                cellprofiler_core.preferences.DEFAULT_INPUT_FOLDER_NAME,
                cellprofiler_core.preferences.ABSOLUTE_FOLDER_NAME,
                cellprofiler_core.preferences.DEFAULT_OUTPUT_SUBFOLDER_NAME,
                cellprofiler_core.preferences.DEFAULT_INPUT_SUBFOLDER_NAME,
            ],
            doc="""\
*(Used only when using an SQLite database, and/or creating a
properties or workspace file)*

This setting determines where the SQLite database is
saved if you decide to write measurements to files instead of writing
them directly to a database. If you request a CellProfiler Analyst
properties file or workspace file, it will also be saved to this
location.

{IO_FOLDER_CHOICE_HELP_TEXT}

{IO_WITH_METADATA_HELP_TEXT}
""".format(
                **{
                    "IO_FOLDER_CHOICE_HELP_TEXT": IO_FOLDER_CHOICE_HELP_TEXT,
                    "IO_WITH_METADATA_HELP_TEXT": _help.IO_WITH_METADATA_HELP_TEXT,
                }
            ),
        )

        self.directory.dir_choice = (
            cellprofiler_core.preferences.DEFAULT_OUTPUT_FOLDER_NAME
        )

        self.save_cpa_properties = cellprofiler_core.setting.Binary(
            "Create a CellProfiler Analyst properties file?",
            False,
            doc="""\
Select "*{YES}*" to generate a template properties file that will allow
you to use your new database with CellProfiler Analyst (a data
exploration tool which can also be downloaded from
http://www.cellprofiler.org/). The module will attempt to fill in as
many entries as possible based on the pipeline’s settings, including the
server name, username, and password if MySQL is used. Keep in mind you
should not share the resulting file because it contains your password.
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.location_object = cellprofiler_core.setting.ObjectNameSubscriber(
            "Which objects should be used for locations?",
            "None",
            doc="""\
*(Used only if creating a properties file)*

CellProfiler Analyst displays cells (or other biological objects of
interest) during classification. This
setting determines which object centers will be used as the center of
the cells/objects to be displayed. Choose one of the listed objects and
CellProfiler will save that object’s location columns in the
properties file so that CellProfiler Analyst centers cells/objects using that
object’s center.

You can manually change this choice in the properties file by editing
the *cell\_x\_loc* and *cell\_y\_loc* properties.

Note that if there are no objects defined in the pipeline (e.g., if only
using MeasureImageQuality and/or Illumination Correction modules), a
warning will display until you choose *‘None’* for the subsequent
setting: ‘Export measurements for all objects to the database?’.
"""
            % globals(),
        )

        self.wants_properties_image_url_prepend = cellprofiler_core.setting.Binary(
            "Access CellProfiler Analyst images via URL?",
            False,
            doc="""\
*(Used only if creating a properties file)*

The image paths written to the database will be the absolute path the
image files on your computer. If you plan to make these files accessible
via the web, you can have CellProfiler Analyst prepend a URL to your
file name. E.g., if an image is loaded from the path
``/cellprofiler/images/`` and you use a url prepend of
``http://mysite.com/``, CellProfiler Analyst will look for your file at
``http://mysite.com/cellprofiler/images/``  """,
        )
        #
        # Hack: if user is on Broad IP, then plug in the imageweb url prepend
        #
        import socket

        try:
            fqdn = socket.getfqdn()
        except:
            fqdn = "127.0.0.1"
        default_prepend = ""
        if "broadinstitute" in fqdn.lower():  # Broad
            default_prepend = "http://imageweb/images/CPALinks"

        self.properties_image_url_prepend = cellprofiler_core.setting.Text(
            "Enter an image url prepend if you plan to access your files via http",
            default_prepend,
            doc="""\
*(Used only if accessing CellProfiler Analyst images via URL)*

The image paths written to the database will be the absolute path the
image files on your computer. If you plan to make these files
accessible via the web, you can enter a url prefix here. E.g., if an
image is loaded from the path ``/cellprofiler/images/`` and you use a
url prepend of ``http://mysite.com/``, CellProfiler Analyst will look
for your file at ``http://mysite.com/cellprofiler/images/``

If you are not using the web to access your files (i.e., they are
locally accessible by your computer), leave this setting blank.""",
        )

        self.properties_plate_type = cellprofiler_core.setting.Choice(
            "Select the plate type",
            PLATE_TYPES,
            doc="""\
*(Used only if creating a properties file)*

If you are using a multi-well plate or microarray, you can select the
plate type here. Supported types in CellProfiler Analyst are 96- and
384-well plates, as well as 5600-spot microarrays. If you are not using
a plate or microarray, select *None*.""",
        )

        self.properties_plate_metadata = cellprofiler_core.setting.Choice(
            "Select the plate metadata",
            ["None"],
            choices_fn=self.get_metadata_choices,
            doc="""\
*(Used only if creating a properties file)*

If you are using a multi-well plate or microarray, you can select the
metadata corresponding to the plate here. If there is no plate
metadata associated with the image set, select *None*.

{USING_METADATA_HELP_REF}
""".format(
                **{"USING_METADATA_HELP_REF": _help.USING_METADATA_HELP_REF}
            ),
        )

        self.properties_well_metadata = cellprofiler_core.setting.Choice(
            "Select the well metadata",
            ["None"],
            choices_fn=self.get_metadata_choices,
            doc="""\
*(Used only if creating a properties file)*

If you are using a multi-well plate or microarray, you can select the
metadata corresponding to the well here. If there is no well metadata
associated with the image set, select *None*.

{USING_METADATA_HELP_REF}
""".format(
                **{"USING_METADATA_HELP_REF": _help.USING_METADATA_HELP_REF}
            ),
        )

        self.properties_export_all_image_defaults = cellprofiler_core.setting.Binary(
            "Include information for all images, using default values?",
            True,
            doc="""\
*(Used only if creating a properties file)*

Select "*{YES}*" to include information in the properties file for all
images. This option will do the following:

-  All images loaded using the **Input** modules or saved in
   **SaveImages** will be included.
-  The CellProfiler image name will be used for the *image\_name* field.
-  A channel color listed in the *image\_channel\_colors* field will be
   assigned to the image by default order.

Select "*{NO}*" to specify which images should be included or to
override the automatic values.""".format(
                **{"YES": "Yes", "NO": "No"}
            ),
        )

        self.image_groups = []
        self.image_group_count = cellprofiler_core.setting.HiddenCount(
            self.image_groups, "Properties image group count"
        )
        self.add_image_group(False)
        self.add_image_button = cellprofiler_core.setting.DoSomething(
            "", "Add another image", self.add_image_group
        )

        self.properties_wants_groups = cellprofiler_core.setting.Binary(
            "Do you want to add group fields?",
            False,
            doc="""\
*(Used only if creating a properties file)*

**Please note that “groups” as defined by CellProfiler Analyst has
nothing to do with “grouping” as defined by CellProfiler in the Groups
module.**

Select "*{YES}*" to define a “group” for your image data (for example,
when several images represent the same experimental sample), by
providing column(s) that identify unique images (the *image key*) to
another set of columns (the *group key*).

The format for a group in CellProfiler Analyst is:

``group_SQL_<XXX> = <MySQL SELECT statement that returns image-key columns followed by group-key columns>``

For example, if you wanted to be able to group your data by unique
plate names, you could define a group called *SQL\_Plate* as follows:

``group_SQL_Plate = SELECT ImageNumber, Image_Metadata_Plate FROM Per_Image``

Grouping is useful, for example, when you want to aggregate counts for
each class of object and their scores on a per-group basis (e.g.,
per-well) instead of on a per-image basis when scoring with the
Classifier function within CellProfiler Analyst.
It will also provide new options in the Classifier fetch menu so you can
fetch objects from images with specific values for the group columns.
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.group_field_groups = []
        self.group_field_count = cellprofiler_core.setting.HiddenCount(
            self.group_field_groups, "Properties group field count"
        )
        self.add_group_field_group(False)
        self.add_group_field_button = cellprofiler_core.setting.DoSomething(
            "", "Add another group", self.add_group_field_group
        )

        self.properties_wants_filters = cellprofiler_core.setting.Binary(
            "Do you want to add filter fields?",
            False,
            doc="""\
*(Used only if creating a properties file)*

Select "*{YES}*" to specify a subset of the images in your experiment by
defining a *filter*. Filters are useful, for example, for fetching and
scoring objects in Classifier within CellProfiler Analyst or making graphs using the plotting tools
that satisfy a specific metadata constraint.
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.create_filters_for_plates = cellprofiler_core.setting.Binary(
            "Automatically create a filter for each plate?",
            False,
            doc="""\
*(Used only if creating a properties file and specifying an image data filter)*

If you have specified a plate metadata tag, select "*{YES}*" to
create a set of filters in the properties file, one for each plate.
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.filter_field_groups = []
        self.filter_field_count = cellprofiler_core.setting.HiddenCount(
            self.filter_field_groups, "Properties filter field count"
        )
        self.add_filter_field_button = cellprofiler_core.setting.DoSomething(
            "", "Add another filter", self.add_filter_field_group
        )

        self.properties_class_table_name = cellprofiler_core.setting.Text(
            "Enter a phenotype class table name if using the Classifier tool in CellProfiler Analyst",
            "",
            doc="""\
*(Used only if creating a properties file)*

If you are using the machine-learning tool Classifier in CellProfiler Analyst,
you can create an additional table in your database that contains the
per-object phenotype labels. This table is produced after scoring all
the objects in your data set and will be named with the label given
here. Note that the actual class table will be named by prepending the
table prefix (if any) to what you enter here.

You can manually change this choice in the properties file by editing
the *class\_table* field. Leave this field blank if you are not using
Classifier or do not need the table written to the database.""",
        )

        self.properties_classification_type = cellprofiler_core.setting.Choice(
            "Select the classification type",
            CLASSIFIER_TYPE,
            doc="""\
*(Used only if creating a properties file)*

Choose the type of classification this properties file will be used
for. This setting will create and set a field called
*classification\_type*. Note that if you will not be using the Classifier
tool in CellProfiler Analyst, this setting will be ignored.

-  *{CT_OBJECT}:* Object-based classification, i.e., set
   *classification\_type* to “object” (or leave it blank).
-  *{CT_IMAGE}:* Image-based classification, e.g., set
   *classification\_type* to “image”.

You can manually change this choice in the properties file by editing
the *classification\_type* field.
""".format(
                **{"CT_OBJECT": CT_OBJECT, "CT_IMAGE": CT_IMAGE}
            ),
        )

        self.create_workspace_file = cellprofiler_core.setting.Binary(
            "Create a CellProfiler Analyst workspace file?",
            False,
            doc="""\
*(Used only if creating a properties file)*

Choose the type of classification this properties file will be used
for. This setting will create and set a field called
*classification\_type*. Note that if you are not using the classifier
tool, this setting will be ignored.

-  *{CT_OBJECT}:* Object-based classification, i.e., set
   *classification\_type* to “object” (or leave it blank).
-  *{CT_IMAGE}:* Image-based classification, e.g., set
   *classification\_type* to “image”.

You can manually change this choice in the properties file by editing
the *classification\_type* field.
""".format(
                **{"CT_OBJECT": CT_OBJECT, "CT_IMAGE": CT_IMAGE}
            ),
        )

        self.divider = cellprofiler_core.setting.Divider(line=True)
        self.divider_props = cellprofiler_core.setting.Divider(line=True)
        self.divider_props_wkspace = cellprofiler_core.setting.Divider(line=True)
        self.divider_wkspace = cellprofiler_core.setting.Divider(line=True)

        self.workspace_measurement_groups = []
        self.workspace_measurement_count = cellprofiler_core.setting.HiddenCount(
            self.workspace_measurement_groups, "Workspace measurement count"
        )

        def add_workspace_measurement_group(can_remove=True):
            self.add_workspace_measurement_group(can_remove)

        add_workspace_measurement_group(False)
        self.add_workspace_measurement_button = cellprofiler_core.setting.DoSomething(
            "", "Add another measurement", self.add_workspace_measurement_group
        )

        self.mysql_not_available = cellprofiler_core.setting.Divider(
            "Cannot write to MySQL directly - CSV file output only",
            line=False,
            doc="""The MySQLdb python module could not be loaded.  MySQLdb is necessary for direct export.""",
        )

        self.db_host = cellprofiler_core.setting.Text(
            text="Database host",
            value="",
            doc="""Enter the address CP must contact to write to the database.""",
        )

        self.db_user = cellprofiler_core.setting.Text(
            text="Username", value="", doc="""Enter your database username."""
        )

        self.db_passwd = cellprofiler_core.setting.Text(
            text="Password",
            value="",
            doc="""Enter your database password. Note that this will be saved in your pipeline file and thus you should never share the pipeline file with anyone else.""",
        )

        self.sqlite_file = cellprofiler_core.setting.Text(
            "Name the SQLite database file",
            "DefaultDB.db",
            doc="""\
*(Used if SQLite selected as database type)*

Enter the name of the SQLite database filename to which you want to write.""",
        )

        self.wants_agg_mean = cellprofiler_core.setting.Binary(
            "Calculate the per-image mean values of object measurements?",
            True,
            doc="""\
Select "*{YES}*" for **ExportToDatabase** to calculate population
statistics over all the objects in each image and store the results in
the database. For instance, if you are measuring the area of the Nuclei
objects and you check the box for this option, **ExportToDatabase** will
create a column in the Per\_Image table called
“Mean\_Nuclei\_AreaShape\_Area”.

You may not want to use **ExportToDatabase** to calculate these
population statistics if your pipeline generates a large number of
per-object measurements; doing so might exceed database column limits.
These columns can be created manually for selected measurements directly
in MySQL. For instance, the following SQL command creates the
Mean\_Nuclei\_AreaShape\_Area column:

``ALTER TABLE Per_Image ADD (Mean_Nuclei_AreaShape_Area); UPDATE Per_Image SET
Mean_Nuclei_AreaShape_Area = (SELECT AVG(Nuclei_AreaShape_Area) FROM Per_Object
WHERE Per_Image.ImageNumber = Per_Object.ImageNumber);`` 
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.wants_agg_median = cellprofiler_core.setting.Binary(
            "Calculate the per-image median values of object measurements?",
            False,
            doc="""\
Select "*{YES}*" for **ExportToDatabase** to calculate population
statistics over all the objects in each image and store the results in
the database. For instance, if you are measuring the area of the Nuclei
objects and you check the box for this option, **ExportToDatabase** will
create a column in the Per\_Image table called
“Median\_Nuclei\_AreaShape\_Area”.

You may not want to use **ExportToDatabase** to calculate these
population statistics if your pipeline generates a large number of
per-object measurements; doing so might exceed database column limits.
However, unlike population means and standard deviations, there is no
built in median operation in MySQL to create these values manually.
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.wants_agg_std_dev = cellprofiler_core.setting.Binary(
            "Calculate the per-image standard deviation values of object measurements?",
            False,
            doc="""\
Select "*{YES}*" for **ExportToDatabase** to calculate population
statistics over all the objects in each image and store the results in
the database. For instance, if you are measuring the area of the Nuclei
objects and you check the box for this option, **ExportToDatabase** will
create a column in the Per\_Image table called
“StDev\_Nuclei\_AreaShape\_Area”.

You may not want to use **ExportToDatabase** to calculate these
population statistics if your pipeline generates a large number of
per-object measurements; doing so might exceed database column limits.
These columns can be created manually for selected measurements directly
in MySQL. For instance, the following SQL command creates the
StDev\_Nuclei\_AreaShape\_Area column:

``ALTER TABLE Per_Image ADD (StDev_Nuclei_AreaShape_Area); UPDATE Per_Image SET
StDev_Nuclei_AreaShape_Area = (SELECT STDDEV(Nuclei_AreaShape_Area) FROM Per_Object
WHERE Per_Image.ImageNumber = Per_Object.ImageNumber);`` 
""".format(
                **{"YES": "Yes"}
            ),
        )

        self.wants_agg_mean_well = cellprofiler_core.setting.Binary(
            "Calculate the per-well mean values of object measurements?",
            False,
            doc="""\
*(Used only if {DB_MYSQL} is selected as database type)*

Select "*{YES}*" for **ExportToDatabase** to calculate statistics over
all the objects in each well and store the results as columns in a
“per-well” table in the database. For instance, if you are measuring the
area of the Nuclei objects and you check the aggregate mean box in this
module, **ExportToDatabase** will create a table in the database called
“Per\_Well\_avg”, with a column called “Mean\_Nuclei\_AreaShape\_Area”.
Selecting all three aggregate measurements will create three per-well
tables, one for each of the measurements.

The per-well functionality will create the appropriate lines in a .SQL
file, which can be run on your Per-Image and Per-Object tables to create
the desired per-well table.

Note that this option is only available if you have extracted plate and
well metadata from the filename using the **Metadata** or **LoadData**
modules. It will write out a .sql file with the statements necessary to
create the Per\_Well table, regardless of the option chosen above.
{USING_METADATA_HELP_REF}
""".format(
                **{
                    "DB_MYSQL": DB_MYSQL,
                    "YES": "Yes",
                    "USING_METADATA_HELP_REF": _help.USING_METADATA_HELP_REF,
                }
            ),
        )

        self.wants_agg_median_well = cellprofiler_core.setting.Binary(
            "Calculate the per-well median values of object measurements?",
            False,
            doc="""\
*(Used only if {DB_MYSQL} is selected as database type)*

Select "*{YES}*" for **ExportToDatabase** to calculate statistics over
all the objects in each well and store the results as columns in a
“per-well” table in the database. For instance, if you are measuring the
area of the Nuclei objects and you check the aggregate median box in
this module, **ExportToDatabase** will create a table in the database
called “Per\_Well\_median”, with a column called
“Median\_Nuclei\_AreaShape\_Area”. Selecting all three aggregate
measurements will create three per-well tables, one for each of the
measurements.

The per-well functionality will create the appropriate lines in a .SQL
file, which can be run on your Per-Image and Per-Object tables to create
the desired per-well table.

Note that this option is only available if you have extracted plate and
well metadata from the filename using the **Metadata** or **LoadData**
modules. It will write out a .sql file with the statements necessary to
create the Per\_Well table, regardless of the option chosen above.
{USING_METADATA_HELP_REF}
""".format(
                **{
                    "DB_MYSQL": DB_MYSQL,
                    "YES": "Yes",
                    "USING_METADATA_HELP_REF": _help.USING_METADATA_HELP_REF,
                }
            ),
        )

        self.wants_agg_std_dev_well = cellprofiler_core.setting.Binary(
            "Calculate the per-well standard deviation values of object measurements?",
            False,
            doc="""\
*(Used only if {DB_MYSQL} is selected as database type)*

Select "*{YES}*" for **ExportToDatabase** to calculate statistics over
all the objects in each well and store the results as columns in a
“per-well” table in the database. For instance, if you are measuring the
area of the Nuclei objects and you check the aggregate standard
deviation box in this module, **ExportToDatabase** will create a table
in the database called “Per\_Well\_std”, with a column called
“StDev\_Nuclei\_AreaShape\_Area”. Selecting all three aggregate
measurements will create three per-well tables, one for each of the
measurements.

The per-well functionality will create the appropriate lines in a .SQL
file, which can be run on your Per-Image and Per-Object tables to create
the desired per-well table.

Note that this option is only available if you have extracted plate and
well metadata from the filename using the **Metadata** or **LoadData**
modules. It will write out a .sql file with the statements necessary to
create the Per\_Well table, regardless of the option chosen above.
{USING_METADATA_HELP_REF}
""".format(
                **{
                    "DB_MYSQL": DB_MYSQL,
                    "YES": "Yes",
                    "USING_METADATA_HELP_REF": _help.USING_METADATA_HELP_REF,
                }
            ),
        )

        self.objects_choice = cellprofiler_core.setting.Choice(
            "Export measurements for all objects to the database?",
            [O_ALL, O_NONE, O_SELECT],
            doc="""\
This option lets you choose the objects whose measurements will be saved
in the Per\_Object and Per\_Well(s) database tables.

-  *{O_ALL}:* Export measurements from all objects.
-  *{O_NONE}:* Do not export data to a Per\_Object table. Save only
   Per\_Image or Per\_Well measurements (which nonetheless include
   population statistics from objects).
-  *{O_SELECT}:* Select the objects you want to export from a list.
""".format(
                **{"O_ALL": O_ALL, "O_NONE": O_NONE, "O_SELECT": O_SELECT}
            ),
        )

        self.objects_list = cellprofiler_core.setting.ObjectSubscriberMultiChoice(
            "Select the objects",
            doc="""\
*(Used only if "Select" is chosen for adding objects)*

Choose one or more objects from this list (click using shift or command
keys to select multiple objects). The list includes the objects that
were created by prior modules. If you choose an object, its measurements
will be written out to the Per\_Object and/or Per\_Well(s) tables,
otherwise, the object’s measurements will be skipped.""",
        )

        self.wants_relationship_table_setting = cellprofiler_core.setting.Binary(
            "Export object relationships?",
            True,
            doc="""\
*(Used only for pipelines which relate objects to each other)*

Select "*{YES}*" to export object relationships to the
RelationshipsView view. Only certain modules produce relationships
that can be exported by this setting; see the **TrackObjects**,
**RelateObjects**, **MeasureObjectNeighbors** and the **Identify**
modules for more details.

This view has the following columns:

-  *{COL_MODULE_NUMBER}*: the module number of the module that
   produced the relationship. The first module in the pipeline is module
   #1, etc.
-  *{COL_RELATIONSHIP}*: the relationship between the two objects,
   for instance, “Parent”.
-  *{COL_OBJECT_NAME1}, {COL_OBJECT_NAME2}*: the names of the
   two objects being related.
-  *{COL_IMAGE_NUMBER1}, {COL_OBJECT_NUMBER1}*: the image number
   and object number of the first object in the relationship
-  *{COL_IMAGE_NUMBER2}, {COL_OBJECT_NUMBER2}*: the image number
   and object number of the second object in the relationship
""".format(
                **{
                    "YES": "Yes",
                    "COL_MODULE_NUMBER": COL_MODULE_NUMBER,
                    "COL_RELATIONSHIP": COL_RELATIONSHIP,
                    "COL_OBJECT_NAME1": COL_OBJECT_NAME1,
                    "COL_OBJECT_NAME2": COL_OBJECT_NAME2,
                    "COL_IMAGE_NUMBER1": COL_IMAGE_NUMBER1,
                    "COL_IMAGE_NUMBER2": COL_IMAGE_NUMBER2,
                    "COL_OBJECT_NUMBER1": COL_OBJECT_NUMBER1,
                    "COL_OBJECT_NUMBER2": COL_OBJECT_NUMBER2,
                }
            ),
        )

        self.max_column_size = cellprofiler_core.setting.Integer(
            "Maximum # of characters in a column name",
            64,
            minval=10,
            maxval=64,
            doc="""\
This setting limits the number of characters that can appear in the name
of a field in the database. MySQL has a limit of 64 characters per
field, but also has an overall limit on the number of characters in all
of the columns of a table. **ExportToDatabase** will shorten all of the
column names by removing characters, at the same time guaranteeing that
no two columns have the same name.""",
        )

        self.separate_object_tables = cellprofiler_core.setting.Choice(
            "Create one table per object, a single object table or a single object view?",
            [OT_COMBINE, OT_PER_OBJECT, OT_VIEW],
            doc="""\
**ExportToDatabase** can create either one table for each type of
object exported or a single object table.

-  *{OT_PER_OBJECT}* creates one table for each object type you
   export. The table name will reflect the name of your objects. The
   table will have one row for each of your objects. You can write SQL
   queries that join tables using the “Number\_ObjectNumber” columns of
   parent objects (such as those created by **IdentifyPrimaryObjects**)
   with the corresponding “Parent\_… column” of the child objects.
   Choose *{OT_PER_OBJECT}* if parent objects can have more than one
   child object, if you want a relational representation of your objects
   in the database, or if you need to split columns among different
   tables and shorten column names because of database limitations.
-  *{OT_COMBINE}* creates a single database table that records the
   object measurements. **ExportToDatabase** will prepend each column
   name with the name of the object associated with that column’s
   measurement. Each row of the table will have measurements for all
   objects that have the same image and object number. Choose
   *{OT_COMBINE}* if parent objects have a single child, or if you
   want a simple table structure in your database. You can combine the
   measurements for all or selected objects in this way.
-  *{OT_VIEW}* creates a single database view to contain the object
   measurements. A *view* is a virtual database table which can be used
   to package together multiple per-object tables into a single
   structure that is accessed just like a regular table. Choose
   *{OT_VIEW}* if you want to combine multiple objects but using
   *{OT_COMBINE}* would produce a table that hits the database size
   limitations.
   An important note is that only objects that are related as primary,
   secondary or tertiary objects to each other should be combined in a
   view. This is because the view expects a one-to-one relationship
   between the combined objects. If you are selecting objects for the
   view, the module will warn you if they are not related in this way.
""".format(
                **{
                    "OT_PER_OBJECT": OT_PER_OBJECT,
                    "OT_COMBINE": OT_COMBINE,
                    "OT_VIEW": OT_VIEW,
                }
            ),
        )

        self.want_image_thumbnails = cellprofiler_core.setting.Binary(
            "Write image thumbnails directly to the database?",
            False,
            doc="""\
*(Used only if {DB_MYSQL} or {DB_SQLITE} are selected as database type)*

Select {YES} if you’d like to write image thumbnails directly into the
database. This will slow down the writing step, but will enable new
functionality in CellProfiler Analyst such as quickly viewing images in
the Plate Viewer tool by selecting “thumbnail” from the “Well display”
dropdown.""".format(
                **{"DB_MYSQL": DB_MYSQL, "DB_SQLITE": DB_SQLITE, "YES": "Yes",}
            ),
        )

        self.thumbnail_image_names = cellprofiler_core.setting.ImageNameSubscriberMultiChoice(
            "Select the images for which you want to save thumbnails",
            doc="""\
*(Used only if {DB_MYSQL} or {DB_SQLITE} are selected as database type)*

Select {YES} if you’d like to write image thumbnails directly into the
database. This will slow down the writing step, but will enable new
functionality in CellProfiler Analyst such as quickly viewing images in
the Plate Viewer tool by selecting “thumbnail” from the “Well display”
dropdown.""".format(
                **{"DB_MYSQL": DB_MYSQL, "DB_SQLITE": DB_SQLITE, "YES": "Yes",}
            ),
        )

        self.auto_scale_thumbnail_intensities = cellprofiler_core.setting.Binary(
            "Auto-scale thumbnail pixel intensities?",
            True,
            doc="""\
*(Used only if {DB_MYSQL} or {DB_SQLITE} are selected as database
type and writing thumbnails is selected)*

Select "*{YES}*" if you’d like to automatically rescale the thumbnail
pixel intensities to the range 0-1, where 0 is black/unsaturated, and 1
is white/saturated. """.format(
                **{"DB_MYSQL": DB_MYSQL, "DB_SQLITE": DB_SQLITE, "YES": "Yes",}
            ),
        )

        self.allow_overwrite = cellprofiler_core.setting.Choice(
            "Overwrite without warning?",
            [OVERWRITE_NEVER, OVERWRITE_DATA, OVERWRITE_ALL],
            doc="""\
**ExportToDatabase** creates tables and databases at the start of a
run when writing directly to a MySQL or SQLite database. It writes SQL
scripts and CSVs when not writing directly. It also can write
CellProfiler Analyst property files. In some cases, it is appropriate
to run CellProfiler and append to or overwrite the data in existing
tables, for instance when running several CellProfiler instances that
each process a range of the experiment’s image sets. In other cases,
such as when the measurements to be written have changed, the data
tables must be dropped completely.
You can choose from three options to control overwriting behavior:

-  *{OVERWRITE_NEVER}:* **ExportToDatabase** will ask before dropping
   and recreating tables unless you are running headless. CellProfiler
   will exit if running headless if the tables exist and this option is
   chosen.
-  *{OVERWRITE_DATA}:* **ExportToDatabase** will keep the existing
   tables if present and will overwrite the data. Choose
   *{OVERWRITE_DATA}* if you are breaking your experiment into ranges
   of image sets and running each range on a separate instance of
   CellProfiler.
-  *{OVERWRITE_ALL}:* **ExportToDatabase** will drop previous
   versions of tables at the start of a run. This option is appropriate
   if you are using the **CreateBatchFiles** module; your tables will be
   created by the run that creates the batch data file. The actual
   analysis runs that utilize the ``Batch_data`` file will use the
   existing tables without trying to recreate them.
""".format(
                **{
                    "OVERWRITE_NEVER": OVERWRITE_NEVER,
                    "OVERWRITE_DATA": OVERWRITE_DATA,
                    "OVERWRITE_ALL": OVERWRITE_ALL,
                }
            ),
        )