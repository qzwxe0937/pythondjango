Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> import pandas as pd

data = {'c1': {('r1', 'r1_1'): 10.0, ('r1', 'r1_2'): 11.0, ('r2', 'r2_1'): 12.0, ('r2', 'r2_2'): 13.0},
        'c2': {('r1', 'r1_1'): 20.0, ('r1', 'r1_2'): 21.0, ('r2', 'r2_1'): 22.0, ('r2', 'r2_2'): 23.0},
        'c3': {('r1', 'r1_1'): 30.0, ('r1', 'r1_2'): 31.0, ('r2', 'r2_1'): 32.0, ('r2', 'r2_2'): 33.0}}
df = pd.DataFrame(data)
