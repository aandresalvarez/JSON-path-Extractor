import requests
import json
import pandas as pd
import os
from datetime import datetime
import re
import os
from typing import List, Union, Any, Generator
from collections import namedtuple


def find_all_paths_of_value(value: Any, input_dict: Union[dict, list], path: List[Union[int, str]] = None) -> Generator[List[Union[int, str]], None, None]:
    """
    Recursively searches for a value in a nested dictionary or list and returns a generator yielding all paths to the value.

    Parameters:
    - value (Any): The value to search for.
    - input_dict (Union[dict, list]): The dictionary or list to search in.
    - path (List[Union[int, str]], optional): The path to the current location in the dictionary or list. Defaults to None.

    Returns:
    - Generator yielding lists of keys/indices forming the paths to the value.

    Examples:
    >>> list(find_all_paths_of_value('test value', {'key1': 'test value', 'key2': {'nested_key': 'test value'}}))
    [['key1'], ['key2', 'nested_key']]

    >>> data = {'key1': 'test value', 'key2': {'nested_key': 'test value'}}
    >>> list(find_all_paths_of_value('test value', data))
    [['key1'], ['key2', 'nested_key']]

    >>> data = {'key1': 'test value', 'key2': [{'nested_key': 'test value'}, {'nested_key': 'other value'}]}
    >>> list(find_all_paths_of_value('test value', data))
    [['key1'], ['key2', 0, 'nested_key']]

    >>> data = [{'key1': 'test value'}, {'key2': {'nested_key': 'test value'}}]
    >>> list(find_all_paths_of_value('test value', data))
    [[0, 'key1'], [1, 'key2', 'nested_key']]
    """
    if path is None:
        path = []
    
    if isinstance(input_dict, dict):
        for k, v in input_dict.items():
            new_path = path + [k]
            if v == value:
                yield new_path
            elif isinstance(v, (dict, list)):
                yield from find_all_paths_of_value(value, v, new_path)
    elif isinstance(input_dict, list):
        for idx, item in enumerate(input_dict):
            new_path = path + [idx]
            if item == value:
                yield new_path
            elif isinstance(item, (dict, list)):
                yield from find_all_paths_of_value(value, item, new_path)





def extract_parent_object(json_obj: Union[dict, list], path: List[Union[int, str]], key_or_level: Union[str, int] = None, level: int = None, key: str = None) -> Union[Any, str]:
    """
    Extract the parent object from a nested JSON structure based on the specified path.

    Parameters:
    - json_obj (Union[dict, list]): The nested JSON object, which must be a dictionary or list.
    - path (List[Union[int, str]]): A list containing keys and indices that form the path to the desired object.
    - key_or_level (Union[str, int], optional): A string specifying the key or an integer specifying the level at which to extract the parent object. This can be provided as a positional argument.
    - level (int, optional): An integer specifying the level at which to extract the parent object. This should be provided as a keyword argument.
    - key (str, optional): A string specifying the key at which to extract the parent object. This should be provided as a keyword argument.

    Returns:
    - Union[Any, str]: The parent object or an error message if not found.

    Examples:
    >>> data = {'results': [{'authorships': [{'institutions': [{'display_name': 'test institution'}]}]}]}
    >>> extract_parent_object(data, ['results', 0, 'authorships', 0, 'institutions', 0, 'display_name'], level=6)
    [{'display_name': 'test institution'}]

    >>> data = {'results': [{'authorships': [{'institutions': [{'display_name': 'test institution'}]}]}]}
    >>> extract_parent_object(data, ['results', 0, 'authorships', 0, 'institutions', 0, 'display_name'], key='institutions')
    {'institutions': [{'display_name': 'test institution'}]}

    >>> data = {'results': [{'authorships': [{'institutions': [{'display_name': 'test institution'}]}]}]}
    >>> extract_parent_object(data, ['results', 0, 'authorships', 0, 'institutions', 0, 'display_name'], level=7)
    "Extraction failed."

    >>> data = {'results': [{'authorships': [{'institutions': [{'display_name': 'test institution'}]}]}]}
    >>> extract_parent_object(data, ['results', 0, 'authorships', 0, 'institutions', 0, 'display_name'], key='invalid_key')
    "Key not found in path."
    """

    # Handling the key_or_level parameter, which can be either the key or the level
    if key_or_level is not None:
        if isinstance(key_or_level, int):
            level = key_or_level
        elif isinstance(key_or_level, str):
            key = key_or_level
        else:
            return "The third argument must be either a string (key) or an integer (level)."

    # Validations and stopping_level determination
    if not isinstance(json_obj, (dict, list)):
        return "'json_obj' must be a dictionary or list."
    if (level is None and key is None) or (level is not None and key is not None):
        return "Specify either 'level' or 'key', not both or neither."
    if not isinstance(path, list) or not path:
        return "'path' must be a non-empty list."
    for p in path:
        if not isinstance(p, (int, str)):
            return "Elements in 'path' must be either integers or strings."
    stopping_level = None
    if level is not None:
        if str(level).startswith('0') and level != 0:
            return "'level' should not have leading zeros."
        if not isinstance(level, int) or level <= 0:
            return "'level' must be a positive integer."
        stopping_level = level - 1
        if stopping_level >= len(path):
            return "'level' exceeds the length of the path."
    else:
        if not isinstance(key, str):
            return "'key' must be a string."
        try:
            stopping_level = path.index(key)
        except ValueError:
            return "Key not found in path."

    # Iterative traversal of the path
    current_obj = json_obj
    for current_level, current_key in enumerate(path):
        if current_level == stopping_level:
            return current_obj

        if not isinstance(current_obj, list) and current_key not in current_obj:
            return "Invalid key in path."
        if isinstance(current_obj, list) and (not isinstance(current_key, int) or current_key < 0 or current_key >= len(current_obj)):
            return "Invalid index in path."

        current_obj = current_obj[current_key]

    return "Extraction failed." # This line should never be reached



def find_all_paths_of_key(key: str, json_obj: Union[dict, list], path: List[Union[int, str]] = None) -> Generator[List[Union[int, str]], None, None]:
    """
    Recursively searches for a key in a nested dictionary or list and returns a generator yielding all paths to the key.

    Parameters:
    - key (str): The key to search for.
    - json_obj (Union[dict, list]): The JSON object, which must be a dictionary or list.
    - path (List[Union[int, str]], optional): The path to the current location in the JSON object. Defaults to None.

    Returns:
    - Generator yielding lists of keys/indices forming the paths to the key.

    Examples:
    >>> list(find_all_paths_of_key('nested_key', {'key1': 'value', 'key2': {'nested_key': 'value'}}))
    [['key2', 'nested_key']]
    >>> list(find_all_paths_of_key('key', [{'key': 'value'}, {'key': 'value2'}]))
    [[0, 'key'], [1, 'key']]
    """
    if path is None:
        path = []
    
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            new_path = path + [k]
            if k == key:
                yield new_path
            elif isinstance(v, (dict, list)):
                yield from find_all_paths_of_key(key, v, new_path)
    elif isinstance(json_obj, list):
        for idx, item in enumerate(json_obj):
            new_path = path + [idx]
            yield from find_all_paths_of_key(key, item, new_path)


# Define a named tuple to store the result with additional information
SearchResult = namedtuple("SearchResult", ["value", "path"])

def search_key_in_all_levels(json_obj: Union[dict, list], paths: List[List[Union[int, str]]], search_key: str, case_insensitive: bool = False) -> List[SearchResult]:
    def search_key_in_all_levels(json_obj: Union[dict, list], paths: List[List[Union[int, str]]], search_key: str, case_insensitive: bool = False) -> List[SearchResult]:
        """
        Searches for a key in a nested dictionary or list and returns a list of named tuples containing the value and path to the key.

        Parameters:
        - json_obj (Union[dict, list]): The JSON object, which must be a dictionary or list.
        - paths (List[List[Union[int, str]]]): A list of paths to the key, as returned by find_all_paths_of_key.
        - search_key (str): The key to search for.
        - case_insensitive (bool, optional): Whether to perform a case-insensitive search. Defaults to False.

        Returns:
        - List of named tuples containing the value and path to the key.

        Examples:
        >>> search_key_in_all_levels({'key1': 'value', 'key2': {'nested_key': 'value'}}, [[['key2', 'nested_key']]], 'nested_key')
        [SearchResult(value='value', path=['key2', 'nested_key'])]
        >>> search_key_in_all_levels([{'key': 'value'}, {'key': 'value2'}], [[[0, 'key']], [[1, 'key']]], 'key')
        [SearchResult(value='value', path=[0, 'key']), SearchResult(value='value2', path=[1, 'key'])]

        The returned list of named tuples can be used to access the value and path of the search result. For example:
        >>> results_found_name_all_levels = search_key_in_all_levels(json_obj, paths, 'name')
        >>> results_found_name_all_levels[0].path
        [0, 'data', 0, 'attributes', 'name']
        >>> results_found_name_all_levels[0].value
        'John Doe'
        """
    results = []
    searched_objects = set() # To keep track of already searched objects

    # Convert the search_key to lowercase if case-insensitive search is enabled
    search_key_lower = search_key.lower() if case_insensitive else search_key

    for path in paths:
        # Iterate from the root to the leaf to avoid reversing the result list
        for level in range(len(path) + 1):
            current_path = path[:level]
            current_obj = json_obj
            for p in current_path:
                if isinstance(current_obj, dict):
                    current_obj = current_obj[p]
                elif isinstance(current_obj, list):
                    current_obj = current_obj[int(p)]
                else:
                    # Skip if current_obj is neither dict nor list
                    continue

            # If current_obj is a list, filter only dictionaries for searching
            if isinstance(current_obj, list):
                current_obj = [item for item in current_obj if isinstance(item, dict) and id(item) not in searched_objects]
            elif id(current_obj) in searched_objects:
                continue

            # Check if the search_key exists in the current object (with optional case-insensitive search)
            for obj in current_obj if isinstance(current_obj, list) else [current_obj]:
                if isinstance(obj, dict) and id(obj) not in searched_objects:
                    searched_objects.add(id(obj))
                    found_key = next((k for k in obj.keys() if (k.lower() if case_insensitive else k) == search_key_lower), None)
                    if found_key:
                        result = SearchResult(value=obj[found_key], path=current_path + [found_key])
                        results.append(result)

    return results


def construct_table_with_keys(orcid: str, json_obj: dict, search_value: str, keys_to_search: List[str]) -> pd.DataFrame:
    """
    Constructs a table with the specified keys and the value that was searched for in the JSON object.
    The function searches for the specified value in the JSON object and then searches for each key in the
    list of keys to search for at all levels relative to the path leading to the value. If all keys are found,
    the function adds the row to the table data. The resulting table is returned as a pandas DataFrame.

    Args:
        orcid (str): The ORCID to retrieve works for.
        json_obj (dict): The JSON object to search for the specified value and keys.
        search_value (str): The value to search for in the JSON object.
        keys_to_search (List[str]): The list of keys to search for at all levels relative to the path leading
            to the value.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the extracted data.

    Example:
        Given the following JSON object:
        {
            "name": "John",
            "age": 30,
            "city": "New York",
            "pets": [
                {
                    "name": "Rufus",
                    "type": "dog"
                },
                {
                    "name": "Mittens",
                    "type": "cat"
                }
            ]
        }

        To construct a table with the keys "name" and "type" for the value "Mittens", the following code can be used:

        >>> json_obj = {
        ...     "name": "John",
        ...     "age": 30,
        ...     "city": "New York",
        ...     "pets": [
        ...         {
        ...             "name": "Rufus",
        ...             "type": "dog"
        ...         },
        ...         {
        ...             "name": "Mittens",
        ...             "type": "cat"
        ...         }
        ...     ]
        ... }
        >>> search_value = "Mittens"
        >>> keys_to_search = ["name", "type"]
        >>> construct_table_with_keys(json_obj, search_value, keys_to_search)
            orcid   values      name    type
        0  123456  Mittens  Mittens     cat
    """
    # Find all paths leading to the specified value using the find_all_paths_of_value function
    paths_to_search_value = list(find_all_paths_of_value(search_value, json_obj))

    # List to store the extracted table data
    table_data_all_levels = []

    # Set to track unique rows and exclude duplicates
    unique_rows = set()

    # Iterate through each path found and use search_key_in_all_levels to find the specified keys
    for path in paths_to_search_value:
        row_data = [orcid, search_value]
        all_keys_found = True
        
        # Search for each key in keys_to_search at all levels relative to the path
        for key in keys_to_search:
            key_results = search_key_in_all_levels(json_obj, [path], key)
            if key_results:
                row_data.append(key_results[0].value)
            else:
                all_keys_found = False
                break

        # If all specified keys are found and the row is unique, add it to the table data
        row_tuple = tuple(row_data)
        if all_keys_found and row_tuple not in unique_rows:
            unique_rows.add(row_tuple)
            table_data_all_levels.append(row_data)

    # Define columns for the DataFrame, including the specified keys
    columns = ['orcid', 'values'] + keys_to_search

    # Convert the extracted data to a pandas DataFrame for better visualization
    table_df_all_levels = pd.DataFrame(table_data_all_levels, columns=columns)
    return table_df_all_levels




# Define a function to get works from an ORCID using the OpenAlex API
def get_works_from_orcid(orcid):
    """
    Given an ORCID, returns the works associated with that ORCID.

    Args:
    orcid (str): The ORCID to retrieve works for.

    Returns:
    dict: A dictionary containing the works associated with the given ORCID.
    """
    url = f"https://api.openalex.org/works?filter=author.orcid%3A{orcid}"
    response = requests.get(url)
    works = json.loads(response.text) # convert to json
    return works





#END OF FUNCTION DEFINITIONS


#################### HERE IS WHERE YOU PUT YOUR CODE ####################

    
    
    #From your previous code 
    #Given adictioanry of grants, find all grants with a ORCID not null

data = {
    "Grantee Name": [ "Federico Costa Cycle 1", "Jessica Manning Cycle 1", "Thushan de Silva Cycle 1", "James Berkley Cycle 1"],
    "ORCID": ["0000-0001-6951-2336", "0000-0003-0232-2196", "0000-0002-6498-9212", "0000-0002-1236-849X"],
    "Grantee role in grant": [ "Principal Investigator", "Principal Investigator", "Principal Investigator", "Principal Investigator"],
    "RFA program name": ["Global Grand Challenges initiative", "Global Grand Challenges initiative", "Global Grand Challenges initiative", "Global Grand Challenges initiative"],
    "grant_start_date": [ datetime(2019, 9, 1), datetime(2019, 9, 2), datetime(2019, 9, 3), datetime(2019, 9, 3)],
    "grant_end_date": [datetime(2021, 9, 1), datetime(2021, 9, 2), datetime(2021, 9, 3), datetime(2021, 9, 3)],
    "Country": [ "Brazil", "Cambodia", "Gambia", "Kenya"],
    "Unnamed: 7": [ "100k", "100k", "100k", "100k"]
}

orcids_df = pd.DataFrame(data)
# Remove rows with missing ORCIDs
orcids_df =orcids_df.dropna(subset=['ORCID'])
list_of_orcids = orcids_df['ORCID'].tolist()

####Loop through the ORCIDs and get the works and save them as JSON files

for orcid in list_of_orcids:
    # Convert ORCID to snakecase
    orcid_snakecase = re.sub(r'[^a-zA-Z0-9]', '_', orcid)
    # Get works from ORCID
    works = get_works_from_orcid(orcid) # call the function get_works_from_orcid and pass the orcid , this will return a dictionary with the works
    
    # save works as a json file with ORCID name in snakecase as file name for example 0000_0001_6951_2336.json
    with open(f'{orcid_snakecase}.json', 'w') as f:
        json.dump(works, f) # convert to json and save as file each json file will have the name of the ORCID in snakecase

#We have now a list of json files saved in the current directory with the name of the ORCID in snakecase




#Lets extract the data from one of the json files and save it as a pandas dataframe

# Define the search value and keys to search for
search_value = 'Chan Zuckerberg Initiative, Redwood City, California, USA' # this is the value that we want to search for in the json file
keys_to_search = ['title', 'doi', 'type']# this is the list of keys that we want to extract from the json file
file='0000_0003_0232_2196.json' # this is the name of the json file that we want to extract the data from


# Open the JSON file and save it as a dictionary
with open(file, 'r') as f:
    data = json.load(f)


# Call the construct_table_with_keys function to get a pandas DataFrame 
#see the function definition above to learn how it works
table_df = construct_table_with_keys(data, search_value, keys_to_search)
# Print the pandas DataFrame
print(table_df)
#save the dataframe as a csv file
table_df.to_csv('table1.csv', index=False)





# ###Next we want to loop through the json files and extract the data that we want using the fuctions that we defined above


# # Create a list with the names of the JSON files saved as files in the current directory
# #search in the current directory for all files that end with .json and create a list with the names of those files
# json_files = [pos_json for pos_json in os.listdir() if pos_json.endswith('.json')]






# #Now we use the list of file names to open each file and save the DATA in a list
# # Open the JSON files and save them in a list
# data_list = []
# for i in json_files:    
#     with open(i, 'r') as f:
#         data = json.load(f)
#         data_list.append(data)