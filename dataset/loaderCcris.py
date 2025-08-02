# Created by weimunyap at 08/07/2025

# Feature:  # Enter feature name here
# # Enter feature description here
#
# Scenario:  # Enter scenario name here
# # Enter steps here

import pandas as pd
import chardet
import numpy as np
import json

path_config = "dataset/config/ccris.json"
path = "sampledata/ccris/2012janjun mini.txt"

# reads in the needed configuration
with open(path_config,"r") as config_file:
    config = json.load(config_file)

# Read a portion of the file to detect encoding
with open(path, "rb") as f:
    raw_data = f.read(10000)  # Read first 10,000 bytes
    chart_det_result = chardet.detect(raw_data)

print(f"{chart_det_result["encoding"]} encoding detected in: {path}")

# read the file with the encoding found
df = pd.read_fwf(
        path,
        encoding=chart_det_result["encoding"]
)

# remove the row with horizontal dividers, only searching in the first 5 rows for performance
divider_index, = np.where(
        df.head().apply(lambda col: col.str.fullmatch("-+").all(),
                        axis=1)
)
df.drop(
        index=divider_index,
        inplace=True
)

# remove the rows with all NA columns, usually the final row
df = df[~df.iloc[:,1:].isna().all(axis=1)]

# get the M columns
m_column_mask = df.columns.str.contains(r"^M\d+$")
m_columns = df.columns[m_column_mask]
other_columns = df.columns[~m_column_mask]


# renaming columns
df.rename(
        columns=config["raw_column_name_to_long_column_name"],
        inplace=True
)
mask_date_columns = df.columns.str.contains(r"Date")

# datetime-fy date or datetime columns
for date_column in df.columns[mask_date_columns]:
    try:
        df[date_column] = pd.to_datetime(
                df[date_column],
                dayfirst=True
        )

    except ValueError as err:
        # some date columns might not have timestamp
        df[date_column] = pd.to_datetime(
                df[date_column],
                dayfirst=True,
                format="%d/%m/%Y",
                errors="coerce"
        )

# remove duplicates based on column_keys
df_duplicate_removed = df.groupby(
        config["column_keys"],
        dropna=False,
        sort=False  # important not to sort as row sequence data represent mutually exclusive information
).first()

x = df_duplicate_removed[df_duplicate_removed.index.get_level_values("Name") == "NOOR ASMAH BINTI HASHIM"]
x.to_clipboard()




