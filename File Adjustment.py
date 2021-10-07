import os
import shutil


def main():
    # Generates the parent path. The architecture for this code is based on the idea that all of the code that
    # handles the data is kept in a separate folder, named 'Code'. The parent path contains all the folders with
    # our data of interest.
    parent_path = os.path.dirname(os.getcwd())

    # Gets a list of all the folders in the parent path, each folder of which contains our data.
    parent_list = os.listdir(parent_path)

    # Establishes a location to store all the data we want.
    store_loc = parent_path + '\\Actual Data'

    # This sets our filter for terms we don't want.
    remove_words = ['DA', 'HA4', 'DPV']

    # Sets any folders we want to skip over. 
    skip_folders = ['Code', 'ZIP Files']

    # We'll iterate through every folder in there.
    for i in range(len(parent_list)):
        # Skips over folders we don't want to mess with.
        if parent_list[i] in skip_folders:
            continue
        else:
            # Gets the current folder we're looking at.
            curr_dir = parent_path + '\\' + parent_list[i]

            try:
                # Gets all the file names that are in that current folder.
                file_names = [f for f in os.listdir(curr_dir)
                              if os.path.isfile(os.path.join(curr_dir, f))]
                # Iteratively checks every file.
                for j in range(len(file_names)):
                    # All the files are split by an underscore between each word. If the list contains any of
                    # the words we want removed, then delete it.
                    if len([x for x in file_names[j].split('_') if x in remove_words]) != 0:
                        os.remove(curr_dir + '\\' + file_names[j])
                    # Otherwise, move it to a new location where we consolidate all of the data.
                    else:
                        shutil.move(curr_dir + '\\' + file_names[j], store_loc + '\\' + file_names[j])
            # Skips any files that are not a directory (zip files, etc).
            except NotADirectoryError:
                continue


if __name__ == "__main__":
    main()
