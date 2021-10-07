import os
import pandas as pd
import numpy as np
import shutil


def main():
    parent_path = os.path.dirname(os.getcwd()) + '\\Data'
    mapped_data = pd.read_csv('Mapped Files.csv')
    mapped_set = moving_files(parent_path, mapped_data)
    average_df = processing_data(parent_path, mapped_set)
    mapping_average(average_df, mapped_data)


def moving_files(parent_path, mapped_data):
    # Making a directory to store the data.
    store_dir = parent_path + '\\Mapped Data'
    try:
        os.mkdir(store_dir)
    except OSError:
        # If the directory already exists, don't complain.
        pass

    # First we'll filter out all the duplicate files that were mapped.
    mapped_list = mapped_data['Associated File'].values
    mapped_set = list(set(mapped_list))

    # Checks every file in this now unique set of files.
    for i in range(len(mapped_set)):
        curr_file = mapped_set[i]
        file_name = parent_path + '\\Filtered Data\\' + curr_file
        # Moves them to a new directory so we can keep track of them.
        shutil.copy(file_name, store_dir + '\\' + curr_file)

    return mapped_set


def processing_data(parent_path, mapped_set):
    # This is where we'll store the average data.
    average_df = pd.DataFrame()
    # We use this key to grab a specific month to average over.
    month_key = '05'
    # Since each day is exactly the same amount of data, we can easily spit the month by this number of indices.
    separate_key = 288

    for i in range(len(mapped_set)):
        # Gets the
        curr_file = mapped_set[i]
        file_name = parent_path + '\\Mapped Data\\' + curr_file
        temp_df = pd.read_csv(file_name)
        # Gets all the times associated with the month of interest.
        month_data = temp_df.loc[temp_df['LocalTime'].str.startswith(month_key)]
        # Just a cheap way of adding in the time steps to the average DataFrame.
        if i == 0:
            average_df['LocalTime'] = [x.split(' ')[1] for x in month_data['LocalTime'][0:separate_key]]
        else:
            pass
        # Initialize a temporary DataFrame to store the day-by-day data we'll average.
        day_df = pd.DataFrame()
        # Adding the time steps to the DataFrame.
        day_df['LocalTime'] = [x.split(' ')[1] for x in month_data['LocalTime'][0:separate_key]]
        # For each day in the month:
        for j in range(int(len(month_data) / separate_key)):
            # Adds a new column with the PV output of that day.
            day_df['Day ' + str(j + 1)] = month_data['Power(MW)'][j * separate_key:(j + 1) * separate_key].values
        # Stores the mean in the average DataFrame, sorted by file name.
        average_df[curr_file] = day_df.mean(axis=1)

    # Writes this data out for reference.
    average_df.to_csv('Average Per File.csv')

    return average_df


def mapping_average(average_df, mapped_data):
    # Sets the columns of the data to be the information we want to store in the rows.
    mapped_averages = pd.DataFrame(columns=['Number of Bus', 'ID'] + list(average_df['LocalTime']))

    # Goes through every bus that we need to map to.
    for i in range(len(mapped_data)):
        # Grabs the file that we decided to map to that bus.
        file_name = mapped_data['Associated File'][i]
        # Gets the average from our previously calculated DataFrame.
        average_data = average_df[file_name]
        # Adds the bus number and ID number to the start of this list.
        mapped_averages_data = np.concatenate(([mapped_data['Number of Bus'][i], mapped_data['ID'][i]],
                                               average_data), axis=None)
        # Adds this information to a new row in our DataFrame.
        mapped_averages.loc[i] = mapped_averages_data

    # Transposes the data so now it looks more like PowerWorld data.
    mapped_averages = mapped_averages.T

    # Writes this out to CSV.
    mapped_averages.to_csv('Mapped Averages.csv')


if __name__ == "__main__":
    main()
