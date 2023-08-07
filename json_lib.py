
import pandas as pd
from datetime import datetime
from collections import namedtuple
from typing import List, Union, Any, Generator



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
            if isinstance(v, str):
                v = v.lower()
            if isinstance(value, str):
                value = value.lower()
            if v == value:
                yield new_path
            elif isinstance(v, (dict, list)):
                yield from find_all_paths_of_value(value, v, new_path)
    elif isinstance(input_dict, list):
        for idx, item in enumerate(input_dict):
            new_path = path + [idx]
            if isinstance(item, str):
                item = item.lower()
            if isinstance(value, str):
                value = value.lower()
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