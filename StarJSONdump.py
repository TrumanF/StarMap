import json
import pandas as pd
import numpy as np
from Body import Star
from Properties import FilterProperties
from multiprocessing import Pool
import os.path
import time
star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False)
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

def sort_star_indices(list_to_sort, keys, reverse_flag=False):
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


def find_index2(elements, value, filter_kw):
    left, right = 0, len(elements) - 1
    while left <= right:
        middle = (left + right) // 2
        val = master_star_list[elements[middle]].__getattribute__(filter_kw)
        if val == value:
            return middle
        if val < value:
            left = middle + 1
        elif val > value:
            right = middle - 1


def find_index_min(elements, value, filter_kw):
    left, right = 0, len(elements)-1
    while left < right:
        middle = (left + right) // 2
        val = master_star_list[elements[middle]].__getattribute__(filter_kw)
        # if val == value:
        #     return middle
        if val >= value:
            right = middle
        else:
            left = middle + 1
    return left


def find_index_max(elements, value, filter_kw):
    left, right = 0, len(elements)-1
    while left < right:
        middle = (left + right) // 2
        val = master_star_list[elements[middle]].__getattribute__(filter_kw)
        # if val == value:
        #     return middle
        if val <= value:
            left = middle + 1
        else:
            right = middle
    return right


def exponential_search_right(elements, value, filter_kw):
    if master_star_list[elements[0]].__getattribute__(filter_kw) != value:
        return 0
    i = 1
    while master_star_list[elements[i]].__getattribute__(filter_kw) == value:
        i = i * 2
    return i


def exponential_search_left(elements, value, filter_kw):
    i = -1
    while master_star_list[elements[i]].__getattribute__(filter_kw) == value:
        i = i * 2
    return i


def linear_search(elements, value, filter_kw):
    left_is_set = False
    for i, element in enumerate(elements):
        if master_star_list[element].__getattribute__(filter_kw) == value and not left_is_set:
            left_end = i
            left_is_set = True
        if master_star_list[element].__getattribute__(filter_kw) != value and left_is_set:
            right_end = i-1
            return left_end, right_end


def linear_search_from_index(elements, starting_index, value, filter_kw):
    i = starting_index+1
    while master_star_list[elements[i]].__getattribute__(filter_kw) == value:
        i += 1
    right_end = i

    i = starting_index-1
    while master_star_list[elements[i]].__getattribute__(filter_kw) == value:
        i -= 1
    left_end = i+1
    return left_end, right_end


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

    t = list(range(len(master_star_list)))
    filters = ['mag', 'ra', 'dec', 'dist']
    sorted_lists = {}
    for filter in filters:
        sorted_lists[filter] = sort_star_indices(t, [filter])

    def search_with_exponential(filter_kw, val):
        ind = find_index2(sorted_lists[filter_kw], val, filter_kw)
        print("2: ", ind)
        max_index_expo = exponential_search_right(sorted_lists[filter_kw][ind+1:], val, filter_kw)
        min_index_expo = exponential_search_left(sorted_lists[filter_kw][:ind], val, filter_kw)

        limits = linear_search(sorted_lists[filter_kw][ind+min_index_expo:ind+max_index_expo+1], val, filter_kw)
        print((ind + min_index_expo + limits[0], ind+1 + min_index_expo + limits[1]))
        print([x.__getattribute__(filter_kw) for x in master_star_list[ind + min_index_expo + limits[0]:ind+1 + min_index_expo + limits[1]]])
        print([x.__getattribute__(filter_kw) for x in
               master_star_list[ind + min_index_expo + limits[0] -1:ind + 2 + min_index_expo + limits[1]]])

    def search_outward(filter_kw, val):
        ind_min = find_index_min(sorted_lists[filter_kw], val, filter_kw)
        ind_max = find_index_max(sorted_lists[filter_kw], val, filter_kw)

        return ind_min, ind_max

    def indices_from_filter(filter_prop):
        all_sets = []
        for f_group in filter_prop.filters:
            temp_indices = []
            for f in f_group:
                val = f.value
                type = f.type
                i_range = search_outward(type, val)
                if f.greater_than:
                    temp_indices.append(set(sorted_lists[type][i_range[0 if f.equals else 1]:]))
                if f.less_than:
                    temp_indices.append(set(sorted_lists[type][:i_range[1 if f.equals else 0]]))
            temp_set = set.intersection(*temp_indices)
            all_sets.append(temp_set)
        return set.intersection(*all_sets)

    fp = FilterProperties(['9<=mag<=9.01', f'{0*15}<dec<={12*15}'])
    print(indices_from_filter(fp))


if __name__ == "__main__":
    main()
