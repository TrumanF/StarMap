import json
import pandas as pd
from Body import Star
from multiprocessing import Pool
import os.path
import time
star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False, nrows=100000)
master_star_list = []


def create_star(i) -> Star:
    # Processes star information from main star dataframe (star_df) and returns Star object
    new_star = Star(star_df['ra'][i], star_df['dec'][i], star_df['mag'][i], star_df['hd'][i],
                    star_df['bayer'][i], star_df['dist'][i], star_df['proper'][i],
                    con=star_df['con'][i])
    return new_star


def gen_master_list():
    print("gen master list")
    with Pool() as pool:
        result = pool.map_async(create_star, star_df.index)
        pool.close()
        pool.join()
    for star in result.get():
        master_star_list.append(star)


def unpack(**kwargs):
    for x in kwargs:
        print(x)

@profile
def sort_star_indices(keys, reverse_flag=False):
    """
    Sorts input list according to keys and optional reverse flag.
    Parameters:
    ---------------
    list_to_sort (list):   list of Star() objects to be sorted
    keys (list):   list of attributes of Star() to be sorted by
    reverse_flag (bool):   (optional) True indicates the list should be sorted backwards
    NOTE: As it stands, this reverse flag applies to ALL keys.
    ---------------
    returns List of sorted Star() objects
    """

    # Note: Sorted() sucks, can't tell it which key needs to be reversed, just deal with it for now
    def sort_star_tuple(star_tuple):
        final = []
        for key in keys:
            final.append(star_tuple[1].__getattribute__(key))
        return tuple(final)

    temp = sorted(list(enumerate(master_star_list)), key=sort_star_tuple, reverse=reverse_flag)
    return [x[0] for x in temp]

@profile
def sort_star_indices2(list_to_sort, keys, reverse_flag=False):
    """
    Sorts input list according to keys and optional reverse flag.
    Parameters:
    ---------------
    list_to_sort (list):   list of Star() objects to be sorted
    keys (list):   list of attributes of Star() to be sorted by
    reverse_flag (bool):   (optional) True indicates the list should be sorted backwards
    NOTE: As it stands, this reverse flag applies to ALL keys.
    ---------------
    returns List of sorted Star() objects
    """

    # Note: Sorted() sucks, can't tell it which key needs to be reversed, just deal with it for now
    def sort_star_tuple(star_tuple):
        final = []
        for key in keys:
            final.append(star_tuple[0].__getattribute__(key))
        return tuple(final)

    temp = sorted([(master_star_list[i], i) for i in list_to_sort], key=sort_star_tuple, reverse=reverse_flag)
    return [x[1] for x in temp]

@profile
def main():
    time1 = time.time()
    if os.path.isfile("master_star_list.json"):
        with open("master_star_list.json", "r") as openfile:
            json_object = json.load(openfile)
        for obj in json_object:
            master_star_list.append(Star.from_dict(**obj))
        time2 = time.time()
    else:
        gen_master_list()
        jsonString = json.dumps([x.__dict__ for x in master_star_list])
        with open("master_star_list.json", "w") as outfile:
            outfile.write(jsonString)
        time2 = time.time()
    # print(master_star_list[0:5])
    # print(len(master_star_list))
    # print(f'Time: {time2 - time1}')

    t = list(range(len(master_star_list)))
    filters = ['mag', 'ra', 'dec', 'dist']
    sorted_lists = {}
    sorted_lists2 = {}
    for filter in filters:
        sorted_lists[filter] = sort_star_indices([filter])
    for filter in filters:
        sorted_lists2[filter] = sort_star_indices2(t, [filter])
    print(sorted_lists['dist'][:100])
    print(sorted_lists2['dist'][:100])

if __name__ == "__main__":
    main()
