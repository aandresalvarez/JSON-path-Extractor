import requests
import json
from typing import List
import pandas as pd
from json_lib import find_all_paths_of_value, search_key_in_all_levels

#In this example, we will use the same function from the first two examples but extend it to search for multiple values 

#To Run this code in the terminal, use the following command:
# python3 example3.py

def fetch_publications(orcid_id: str) -> dict:
    """
    Fetches the publications associated with a given ORCID.

    Args:
        orcid_id (str): The ORCID to retrieve publications for.

    Returns:
        dict: JSON object containing the publications linked to the given ORCID.
    """
    api_url = f"https://api.openalex.org/works?filter=author.orcid%3A{orcid_id}"
    response = requests.get(api_url)
    return json.loads(response.text)


def extract_data(json_data: dict, target_values: List[str], keys_to_extract: List[str], orcid_id: str):
    """
    Extracts specific data from JSON object and constructs a DataFrame. Searches for a list of target values
    and extracts the corresponding values for specified keys. If all keys are found, the row is added to the DataFrame.

    Args:
        json_data (dict): The JSON object to search and extract data from.
        target_values (List[str]): List of values to search for in the JSON object.
        keys_to_extract (List[str]): List of keys to extract data for.
        orcid_id (str): The ORCID to be added as the first entry in the resulting DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the extracted data.

    Example:
        >>> extract_data(json_data, ['value1', 'value2'], ['title', 'type'], '1234')
    """
    dfs = [] # keep all dataframes

    for target_value in target_values:
        paths_to_target = list(find_all_paths_of_value(target_value, json_data))
        rows = []
        unique_rows = set()

        for path in paths_to_target:
            data = [orcid_id, target_value]
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
        df = pd.DataFrame(rows, columns=['orcid', 'values'] + keys_to_extract)
        dfs.append(df)

    # Concatenate all dataframes
    final_df = pd.concat(dfs, ignore_index=True)
    return final_df 



# Get list of ORCID
orcids = ["0000-0001-6951-2336", "0000-0003-0232-2196", "0000-0002-6498-9212", "0000-0002-1236-849X"]

dfs = [] # keep all dataframes
# Get dataframe with specific data to search for
search_values = ['Chan Zuckerberg Initiative, Redwood City, California, USA', 'Chan Zuckerberg Biohub, 499 Illinois St, San Francisco, CA 94158, USA'] 
keys_to_search = ['title', 'doi', 'type']

for orcid in orcids:
    json_obj = fetch_publications(orcid)
    df = extract_data(json_obj, search_values, keys_to_search, orcid)
    dfs.append(df)



# Concatenate all dataframes
final_df = pd.concat(dfs, ignore_index=True)



# #Remove duplicated doi values
# final_df.drop_duplicates(subset=['doi'], inplace=True)


# Print DataFrame
print(final_df)

# Save DataFrame to CSV
final_df.to_csv('example3_multiple_orcids_multiple_values_output.csv', index=False)