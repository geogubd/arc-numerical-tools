# Name: RoundDateTime.py
# Purpose: Will take a selected datetime field and will round it to the nearest increment denoted for each unit.
# Author: David Wasserman
# Last Modified: 7/24/2016
# Copyright: David Wasserman
# Python Version:   2.7-3.1
# ArcGIS Version: 10.4 (Pro)
# --------------------------------
# Copyright 2016 David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------
# Import Modules
import SharedArcNumericalLib as san
import os, arcpy, datetime
import pandas as pd


# Function Definitions



@san.arc_tool_report
def round_date_time(in_fc, input_field, new_field_name, set_year=None, set_month=None, set_day=None, set_hour=None,
                    set_minute=None, set_second=None):
    """ This function will take in an feature class, and use pandas/numpy to truncate a date time so that the
     passed date-time attributes are set to a target."""
    try:
        # arc_print(pd.__version__) Does not have dt lib.
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(in_fc)
        workspace = os.path.dirname(desc.catalogPath)
        col_new_field = arcpy.ValidateFieldName(san.create_unique_field_name(new_field_name, in_fc), workspace)
        san.add_new_field(in_fc, col_new_field, "DATE")
        OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
        san.arc_print("Creating Pandas Dataframe from input table.")
        query = "{0} {1} {2}".format(arcpy.AddFieldDelimiters(in_fc, input_field), "is NOT", "NULL")
        fcDataFrame = san.arcgis_table_to_dataframe(in_fc, [input_field, col_new_field], query)
        JoinField = arcpy.ValidateFieldName("DFIndexJoin", workspace)
        fcDataFrame[JoinField] = fcDataFrame.index
        try:
            san.arc_print("Creating new date-time column based on field {0}.".format(str(input_field)), True)
            fcDataFrame[col_new_field] = fcDataFrame[input_field].apply(
                lambda dt: san.round_new_datetime(dt, set_year, set_month, set_day, set_hour, set_minute,
                                              set_second)).astype(datetime.datetime)
            del fcDataFrame[input_field]
        except Exception as e:
            del fcDataFrame[input_field]
            san.arc_print(
                "Could not process datetime field. "
                "Check that datetime is a year appropriate to your python version and that "
                "the time format string is appropriate.")
            san.arc_print(e.args[0])
            pass

        san.arc_print("Exporting new time field dataframe to structured numpy array.", True)
        finalStandardArray = fcDataFrame.to_records()
        san.arc_print("Joining new date-time field to feature class.", True)
        arcpy.da.ExtendTable(in_fc, OIDFieldName, finalStandardArray, JoinField, append_only=False)
        san.arc_print("Delete temporary intermediates.")
        del fcDataFrame, finalStandardArray
        san.arc_print("Script Completed Successfully.", True)

    except arcpy.ExecuteError:
        san.arc_print(arcpy.GetMessages(2))
    except Exception as e:
        san.arc_print(e.args[0])

        # End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    InputField = arcpy.GetParameterAsText(1)
    NewTextFieldName = arcpy.GetParameterAsText(2)
    RoundYear = arcpy.GetParameter(3)
    RoundMonth = arcpy.GetParameter(4)
    RoundDay = arcpy.GetParameter(5)
    RoundHour = arcpy.GetParameter(6)
    RoundMinute = arcpy.GetParameter(7)
    RoundSecond = arcpy.GetParameter(8)
    round_date_time(FeatureClass, InputField, NewTextFieldName, RoundYear, RoundMonth, RoundDay, RoundHour, RoundMinute,
                    RoundSecond)
