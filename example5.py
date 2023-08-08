import requests
import json
from typing import List
import pandas as pd
from json_lib import find_all_paths_of_value_substring, search_key_in_all_levels

def fetch_publications(orcid_id: str) -> dict:
    api_url = f"https://api.openalex.org/works?filter=author.orcid%3A{orcid_id}"
    response = requests.get(api_url)
    return json.loads(response.text)

def extract_data(json_data: dict, target_values: List[str], keys_to_extract: List[str], orcid_id: str, match_type="ignore_case"):
    dfs = []

    for target_value in target_values:
        paths_to_target = list(find_all_paths_of_value_substring(target_value, json_data, match_type=match_type))

        rows = []
        unique_rows = set()

        for path, matched_value in paths_to_target:  # Unpack both path and matched_value
            data = [orcid_id, target_value, matched_value, str(path)]  # Include matched_value and path in the data row
            all_keys_found = True
            for key in keys_to_extract:
                key_results = search_key_in_all_levels(json_data, [path], key)
                if key_results:
                    data.append(key_results[0].value)
                else:
                    all_keys_found = False
                    break
            row_tuple = tuple(data)
            if all_keys_found and row_tuple not in unique_rows:
                unique_rows.add(row_tuple)
                rows.append(data)
        df = pd.DataFrame(rows, columns=['orcid', 'searched_value', 'matched_value', 'path'] + keys_to_extract)  # Include 'matched_value' and 'path' in the DataFrame column headers
        dfs.append(df)

    final_df = pd.concat(dfs, ignore_index=True)
    return final_df


orcids = ["0000-0001-6951-2336", "0000-0003-0232-2196", "0000-0002-6498-9212", "0000-0002-1236-849X", "0000-0003-4276-073X", "0000-0002-6775-7919", "0000-0001-8233-3754", "0000-0002-2378-4720", "0000-0002-7629-0636", "0000-0003-4912-9764", "0000-0003-0353-1133", "0000-0002-0905-3980", "0000-0001-6375-262X", "0000-0002-4437-1343", "0000-0002-9108-2261", "0000-0001-7089-0510","0000-0002-1118-4998","0000-0001-8559-452X"]

dfs = []
search_values = ['Chan', 'Zuckerberg', 'CZID', 'Biohub', 'CZI'] 
keys_to_search = ['title', 'doi', 'type']

for orcid in orcids:
    json_obj = fetch_publications(orcid)
    df = extract_data(json_obj, search_values, keys_to_search, orcid, match_type="substring")
    dfs.append(df)

final_df = pd.concat(dfs, ignore_index=True)

print(final_df)
final_df.to_csv('example5_multiple_orcids_substring_search_matched_values_output.csv', index=False)
