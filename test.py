import pandas as pd
from SVG import SVG
# df = pd.read_csv('stars_labels.csv')
# print(df.columns)
# for ind in df.index[:1500]:
#     print(df['ra'][ind], df['dec'][ind], df['mag'][ind], df['proper'][ind])

test = SVG(500, 500)
test.text(100, 100, "Hello!")
test.circle(100, 100, 1)
test.export("textTest.svg")