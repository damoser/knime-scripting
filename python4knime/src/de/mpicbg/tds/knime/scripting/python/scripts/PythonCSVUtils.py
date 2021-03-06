import csv
import array
from types import *

#
#  Reads the first 'count' lines from a CSV file and determines the type of
#  each column.  Returns a dictionary that maps column names to their data type.
#
#  Example use:
#    try:
#       types = infer_column_types(csv_filename, 100)
#       table = create_data_table(...);
#    except:
#       types = infer_column_types(csv_filename, 0)
#       table = create_data_table(...);
#
def infer_column_types(csv_filename, count):
    csv_reader = csv.reader(open(csv_filename, 'rb'), delimiter=',', quotechar='"')
    types = OrderedDict()
    current = 0
    for row in csv_reader:
        # The first row contains column names.  Use them to build the dictionary keys.
        if current == 0:
            for item in row:
                types[item] = NoneType

        elif current < count or count == 0:
            index = 0
            for item in types:
                type = types[item]
                try:
                    int(row[index])
                    if type == NoneType:
                        type = IntType
                except:
                    try:
                        float(row[index])
                        if type == NoneType or type == IntType:
                            type = FloatType
                    except:
                        type = StringType
                types[item] = type
                index += 1
        current += 1
    return types

#
#  Create a table with a properly sized empty list for each column
#
def create_empty_table(csv_filename, types, header_lines):
    table = OrderedDict()
    count = line_count(csv_filename) - header_lines

    for item in types:
        table[item] = count * [None]

    return table

#
#  Build a dictionary that contains a mapping from column name to column type.
#  Assumes the first line of the file contains comma-separated names and the second line
#  contains comma-separated types, e.g. INT, FLOAT, STRING
#
def get_column_types(csv_filename):
    csv_reader = csv.reader(open(csv_filename, 'rb'), delimiter=',', quotechar='"')
    types = OrderedDict()
    current = 0
    for row in csv_reader:
        # The first row contains column names.  Use them to build the dictionary keys.
        if current == 0:
            for item in row:
                types[item] = NoneType
        # The second row contains column types.  Use them to build the dictionary values.
        elif current == 1:
            index = 0
            for item in types:
                itemType = row[index]
                if itemType == "INT":
                    type = IntType
                elif itemType == "FLOAT":
                    type = FloatType
                else:
                    type = StringType

                types[item] = type
                index += 1

            return types

        current += 1

#
#  Create a data table with values from a CSV table.  The types parameter
#  is a dictionary mapping the column name to its type as created by get_column_types
#
def create_data_table(csv_filename, types, header_lines):
    table = create_empty_table(csv_filename, types, header_lines)

    csv_file = open(csv_filename, 'rb')

    csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')

    current = -header_lines
    for row in csv_reader:
        if current >= 0:
            index = 0
            for item in types:
                array = table[item]
                type = types[item]
                value = row[index]

                if value == "":
                    value = None
                elif type == FloatType:
                    value = float(value)
                elif type == IntType:
                    value = int(value)

                array[current] = value

                index += 1
        current += 1

    return table

#
#  Return the number of data lines in the file
#
def line_count(csv_filename):
    # Count the number of lines
    csv_file = open(csv_filename)
    return sum(1 for line in csv_file)
    csv_file.close()


#
#  Read a CSV file into an OrderedDict.  The first line of the file is assumed to be the column names.
#  If read_types is True the second line must contain the column types, otherwise the file will be read
#  to infer the types.
#
def read_csv(csv_filename, read_types):
    if read_types:
        types = get_column_types(csv_filename)
        table = create_data_table(csv_filename, types, 2)
    else:
        try:
            types = infer_column_types(csv_filename, 100)
        except:
            types = infer_column_types(csv_filename, 0)

        table = create_data_table(csv_filename, types, 1)

    return table

#
#  Write a table (dictionary) to a csv file.  The first line will contain a comma-separated list
#  of column names and the second line will contain a comma-separated list of data types.  All subsequent
#  lines will be a row with comma-separated values for each colunn.
#
def write_csv(csv_filename, table, write_types):
    csv_file = open(csv_filename, 'wb')
    csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    keys = table.keys()
    count = len(table[keys[0]])

    #  First write the column headers
    csv_writer.writerow(keys)

    #  Next save the types if desired
    if write_types:
        types = []
        for item in table:
            column = table[item]
            index = 0

            # Find the first non-missing value
            while type(column[index]) is NoneType:
                index += 1

            if type(column[index]) is IntType or type(column[index]) is LongType:
                types.append("INT")
            elif type(column[index]) is FloatType:
                types.append("FLOAT")
            else:
                types.append("STRING")

        csv_writer.writerow(types)

    #  Next write the data values, row by row
    for current in range(count):
        row = []
        for item in table:
            column = table[item]
            value = column[current]
            if value is not None:
                row.append(value)
            else:
                row.append("")

        csv_writer.writerow(row)

    csv_file.close()

import platform

# Check for the correct version
version = platform.python_version()
if float(version[:3]) < 2.7:
    from ordereddict import OrderedDict
else:
    from collections import OrderedDict
