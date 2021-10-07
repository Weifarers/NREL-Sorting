import os
import pandas as pd


def main():
    # Generates the parent path. The architecture for this code is based on the idea that all of the code that
    # handles the data is kept in a separate folder, named 'Code'. The parent path contains all the folders with
    # our data of interest.
    parent_path = os.path.dirname(os.getcwd()) + '\\Data'

    nrel_df = import_nrel(parent_path)


def import_nrel(parent_path):
    # This function will read in all the data we got from NREL (after it's been filtered), and store it in
    # pandas DataFrame for our reference.

    # First we look at the directory where all the filtered data is.
    source_dir = parent_path + '\\Filtered Data'

    # Gets all the files that are in the folder.
    file_names = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

    # Initialize a DataFrame that we'll store all the latitudes and longitudes in.
    nrel_df = pd.DataFrame(columns=['Rating', 'Latitude', 'Longitude'])

    for i in range(len(file_names)):
        # Each file is named the same, so we split the name up into its components, separating by an underscore.
        curr_file = file_names[i].split('_')
        # The information we want is always in the same spot, so we hard code in the locations.
        latitude = float(curr_file[1])
        longitude = float(curr_file[2])
        rating = curr_file[5]

        # Adding it onto our list.
        nrel_df = nrel_df.append({'Rating': rating, 'Latitude': latitude, 'Longitude': longitude},
                                         ignore_index=True)

    return nrel_df


def map_data(parent_path, nrel_df):
    # Creates a data folder that we'll store the relevant CSVs in.
    try:
        os.mkdir(parent_path + '\\Mapping Data')
    except OSError:
        # If the directory already exists, don't complain.
        pass

    # The structure here is pretty straightforward:
    # 1) Get a list of all the units in the PW system, with their associated latitude and longitude.
    # 2) For each unit, calculate the distance between that unit and all the units in our mapping DataFrame.
    # 3) Get the closest one, and store that information into another DataFrame.
    #   The DataFrame will have a few columns: Bus #/Unit #/Lat/Long/Closest NREL/NREL Lat/NREL Long
    #   We'll write this DataFrame to a CSV, so we can sanity check that the Lat/Long are seemingly close.
    #   Might revisit the File Adjustment.py, and make it so that we write out what files were taken from what state,
    #   and use that information as a sanity check too.
    # 4) After getting all the mappings done, we take all the files from 'Filtered Data' that were mapped, and copy
    #    them over to a new directory.


if __name__ == "__main__":
    main()
