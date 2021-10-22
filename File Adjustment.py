import os
import shutil
import zipfile
import pandas as pd


def main():
    unzip()
    data_filter()


def unzip():
    # Writing this function to unzip all the files for me.
    # Generates the parent path. The architecture for this code is based on the idea that all of the code that
    # handles the data is kept in a separate folder, named 'Code'. The parent path contains all the folders with
    # our data of interest.
    parent_path = os.path.dirname(os.getcwd())
    # Since the ZIP files are always stored in the same place, I'll just hard code in their location.
    zip_dir = parent_path + '\\ZIP Files'

    # Gets all the files that are in the ZIP folder.
    file_names = [f for f in os.listdir(zip_dir) if os.path.isfile(os.path.join(zip_dir, f))]

    # Creates a data folder that we'll store everything in.
    try:
        os.mkdir(parent_path + '\\Data\\Raw Data')
    except OSError:
        # If the directory already exists, don't complain.
        pass

    # Goes through every ZIP file one by one.
    for i in range(len(file_names)):
        # Grabs the current ZIP file.
        current_zip = zip_dir + '\\' + file_names[i]
        # Extracts it to our parent path.
        with zipfile.ZipFile(current_zip, "r") as zip_ref:
            zip_ref.extractall(parent_path + '\\Data\\Raw Data')


def data_filter():
    # Generates the parent path. The architecture for this code is based on the idea that all of the code that
    # handles the data is kept in a separate folder, named 'Code'. The parent path contains all the folders with
    # our data of interest.
    parent_path = os.path.dirname(os.getcwd()) + '\\Data'

    # Gets a list of all the folders in the parent path, each folder of which contains our raw data.
    parent_list = os.listdir(parent_path + '\\Raw Data')

    # Establishes a location to store all the data we want.
    store_dir = parent_path + '\\Filtered Data'
    try:
        os.mkdir(store_dir)
    except OSError:
        # If the directory already exists, don't complain.
        pass

    # This sets our filter for terms we don't want.
    remove_words = ['DA', 'HA4', 'DPV']

    # We write a DataFrame to use as a sanity checker for later, where we store which state the file came from.
    filtered_df = pd.DataFrame(columns=['State', 'File Name'])

    # We'll iterate through every folder in there.
    for i in range(len(parent_list)):
        # Gets the current folder we're looking at.
        curr_dir = parent_path + '\\Raw Data\\' + parent_list[i]

        try:
            # Gets all the file names that are in that current folder.
            file_names = [f for f in os.listdir(curr_dir)
                          if os.path.isfile(os.path.join(curr_dir, f))]
            # Iteratively checks every file.
            for j in range(len(file_names)):
                # All the files are split by an underscore between each word. If the list contains any of
                # the words we want removed, then skip it.
                if len([x for x in file_names[j].split('_') if x in remove_words]) != 0:
                    continue
                # Otherwise, move it to a new location where we consolidate all of the data.
                else:
                    # Storing what state this file came from, as a sanity checker for later.
                    filtered_df = filtered_df.append({'State': parent_list[i][:2],
                                                      'File Name': file_names[j]},
                                                     ignore_index=True)
                    shutil.copy(curr_dir + '\\' + file_names[j], store_dir + '\\' + file_names[j])

                filtered_df.to_csv('Filtered_State.csv', index=False)
        # Skips any files that are not a directory (zip files, etc).
        except NotADirectoryError:
            continue


if __name__ == "__main__":
    main()
