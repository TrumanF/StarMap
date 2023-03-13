import pandas as pd

# star_df = pd.read_csv('Star CSV/hygdata_v3.csv', keep_default_na=False)  # Note: change this magic number to some variable
# cons_dict = {}
# constellations = set(star_df['con'].tolist())
# constellations.remove('')
# print(len(constellations))
# for con_name in constellations:
#     cons_dict[con_name] = []
# print(cons_dict)
# def get_csv_all_constellations():
#     constellations = set(star_df['con'].tolist())
#     for con_name in constellations:
#         df = star_df[star_df['con'].str.contains(con_name)]
#         df.to_csv(f"constellation CSV/{con_name}.csv", index=False)
#
#
# ori_df = pd.read_csv("constellation CSV/Ori.csv", keep_default_na=False)

file = open("constellation lines CSV/Ori_lines.csv", encoding='utf-8-sig')
for line in file.readlines():
    print(line.strip().split(","))
