import os
import pandas as pd
import numpy as np


def main():
    # Generates the parent path. The architecture for this code is based on the idea that all of the code that
    # handles the data is kept in a separate folder, named 'Code'. The parent path contains all the folders with
    # our data of interest.
    parent_path = os.path.dirname(os.getcwd()) + '\\Data'
    # Reading in data.
    pw_df = pd.read_csv('Syn70K_SolarGenBusUnit_LatLong.csv')
    # If there's an empty cell (which gets replaced with "Unnamed: 1") then skip the first row. This is just
    # a rough way to check for that  "Gen" row at the top, and there's probably a better way of doing
    # this check.
    if "Unnamed: 1" in pw_df.columns:
        pw_df = pd.read_csv('Syn70K_SolarGenBusUnit_LatLong.csv', skiprows=1)

    state_df = pd.read_csv('Filtered_State.csv')
    nrel_df = import_nrel(parent_path)
    print("Filtered Data imported.")

    # Does the mapping.
    map_data(nrel_df, pw_df, state_df)


def import_nrel(parent_path):
    # This function will read in all the data we got from NREL (after it's been filtered), and store it in
    # pandas DataFrame for our reference.

    # First we look at the directory where all the filtered data is.
    source_dir = parent_path + '\\Filtered Data'

    # Gets all the files that are in the folder.
    file_names = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

    # Initialize a DataFrame that we'll store all the latitudes and longitudes in.
    nrel_df = pd.DataFrame(columns=['Rating', 'Latitude', 'Longitude', 'File Name'])

    for i in range(len(file_names)):
        # Each file is named the same, so we split the name up into its components, separating by an underscore.
        curr_file = file_names[i].split('_')
        # The information we want is always in the same spot, so we hard code in the locations.
        latitude = float(curr_file[1])
        longitude = float(curr_file[2])
        rating = curr_file[5]

        # Adding it onto our list.
        nrel_df = nrel_df.append({'Rating': rating, 'Latitude': latitude,
                                  'Longitude': longitude, 'File Name': file_names[i]},
                                   ignore_index=True)

    return nrel_df


def map_data(nrel_df, pw_df, state_df):
    # Initializing some values for comparison.
    prev_lat = 0
    prev_long = 0
    min_norm_idx = 0

    # This dataFrame is used as a sanity check for after everything is done, and is written out to an Excel file.
    data_df = pd.DataFrame(columns=['Number of Bus', 'ID', 'Substation Latitude', 'Substation Longitude',
                                    'NREL Rating', 'NREL Latitude', 'NREL Longitude', 'State', 'File'])

    # We'll use this data frame to store what file was mapped to what bus.
    map_df = pd.DataFrame(columns=['Number of Bus', 'ID', 'Associated File'])

    for i in range(len(pw_df)):
        # Temporary DataFrame to store the norms.
        temp_df = pd.DataFrame(columns=['Number of Bus', 'ID', 'Norm', 'Associated File'])
        # Get the current PW lat/long.
        curr_pw_lat = pw_df.loc[i]['Substation Latitude']
        curr_pw_long = pw_df.loc[i]['Substation Longitude']
        if curr_pw_lat == prev_lat and curr_pw_long == prev_long:
            # Stores the file that's been mapped to that bus to our DataFrame.
            map_df = map_df.append({'Number of Bus': pw_df.loc[i]['Number of Bus'], 'ID': pw_df.loc[i]['ID'],
                                    'Associated File': nrel_df.loc[min_norm_idx]['File Name']},
                                   ignore_index=True)

            # Gets the state associated with the file, to be used as a sanity check.
            state_idx = state_df[state_df['File Name'] == nrel_df.loc[min_norm_idx]['File Name']].index.values[0]

            # Stores this in our reference data frame.
            data_df = data_df.append({'Number of Bus': pw_df.loc[i]['Number of Bus'], 'ID': pw_df.loc[i]['ID'],
                                      'Substation Latitude': pw_df.loc[i]['Substation Latitude'],
                                      'Substation Longitude': pw_df.loc[i]['Substation Longitude'],
                                      'NREL Rating': nrel_df.loc[min_norm_idx]['Rating'],
                                      'NREL Latitude': nrel_df.loc[min_norm_idx]['Latitude'],
                                      'NREL Longitude': nrel_df.loc[min_norm_idx]['Longitude'],
                                      'State': state_df.loc[state_idx]['State'],
                                      'File': nrel_df.loc[min_norm_idx]['File Name']},
                                     ignore_index=True)
            # Just outputting what the mapping is.
            print('Mapped Bus Number ' + str(int(pw_df.loc[i]['Number of Bus']))
                  + ' to File: ' + nrel_df.loc[min_norm_idx]['File Name'])

            # Then sets the previous latitude and longitude to our current one. This is so we can skip out on buses that
            # have the same latitude and longitude, and just map them to the same file.
            prev_lat = curr_pw_lat
            prev_long = curr_pw_long
        else:
            # Now we cycle through all the NREL substations.
            for j in range(len(nrel_df)):
                # Gets the associated latitude and longitude.
                curr_nrel_lat = nrel_df.loc[j]['Latitude']
                curr_nrel_long = nrel_df.loc[j]['Longitude']
                # Calculates the Euclidean norm. This is just a rough implementation of it.
                norm_val = np.sqrt(np.square(curr_pw_lat - curr_nrel_lat) + np.square(curr_pw_long - curr_nrel_long))
                # Appends this to our temporary DataFrame.
                temp_df = temp_df.append({'Number of Bus': pw_df.loc[i]['Number of Bus'], 'ID': pw_df.loc[i]['ID'],
                                          'Norm': norm_val, 'Associated File': nrel_df.loc[j]['File Name']},
                                         ignore_index=True)

            # Gets the index associated with the minimum Euclidean Norm.
            min_norm_idx = temp_df['Norm'].idxmin()

            # Stores the file that's been mapped to that bus to our DataFrame.
            map_df = map_df.append({'Number of Bus': pw_df.loc[i]['Number of Bus'], 'ID': pw_df.loc[i]['ID'],
                                    'Associated File': nrel_df.loc[min_norm_idx]['File Name']},
                                   ignore_index=True)

            # Gets the state associated with the file, to be used as a sanity check.
            state_idx = state_df[state_df['File Name'] == nrel_df.loc[min_norm_idx]['File Name']].index.values[0]

            # Stores this in our reference data frame.
            data_df = data_df.append({'Number of Bus': pw_df.loc[i]['Number of Bus'], 'ID': pw_df.loc[i]['ID'],
                                      'Substation Latitude': pw_df.loc[i]['Substation Latitude'],
                                      'Substation Longitude': pw_df.loc[i]['Substation Longitude'],
                                      'NREL Rating': nrel_df.loc[min_norm_idx]['Rating'],
                                      'NREL Latitude': nrel_df.loc[min_norm_idx]['Latitude'],
                                      'NREL Longitude': nrel_df.loc[min_norm_idx]['Longitude'],
                                      'State': state_df.loc[state_idx]['State'],
                                      'File': nrel_df.loc[min_norm_idx]['File Name']},
                                     ignore_index=True)
            # Just outputting what the mapping is.
            print('Mapped Bus Number ' + str(int(pw_df.loc[i]['Number of Bus']))
                  + ' to File: ' + nrel_df.loc[min_norm_idx]['File Name'])
            # Then sets the previous latitude and longitude to our current one. This is so we can skip out on buses that
            # have the same latitude and longitude, and just map them to the same file.
            prev_lat = curr_pw_lat
            prev_long = curr_pw_long

    # Writes these out to excel files.
    map_df.to_csv('Mapped Files.csv', index=False)
    data_df.to_csv('Reference Data.csv', index=False)


if __name__ == "__main__":
    main()
