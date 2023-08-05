# JSON-path-Extractor

This Python project provides a set of functionalities in `json_lib.py` to search for and extract data from nested JSON structures. It does so by finding all paths to a specific value, all paths to a specific key, extracting an ancestor object from a given path, and searching for a key across all depths. Three examples applications are provided to demonstrate the usage of the library.

## Libraries and Dependencies

This project uses the following Python libraries:

- `pandas`: To handle data in form of DataFrame
- `requests`: To fetch JSON data via API calls
- `json`: To work with JSON structure
- `typing`: To add variable type annotations
- `collections`: To use namedtuple

## Code Files

- `json_lib.py`: Contains four methods to extend the functionality of the JSON operation. Utilities include `find_all_paths_of_value()`, `extract_parent_object()`,`find_all_paths_of_key()`, and `search_key_in_all_levels()`.

- `example1.py`: Demonstrates how to fetch JSON data from an API (here, fetch publications by a given ORCID), and sight a specific data and record the data against some keys. The result data is shown and saved as CSV.   

- `example2.py`: Is an extension of `example1.py` to manage several orcids. The rest of the process is the same. The resulting dataframe includes records from all ORCIDs.

- `example3.py`: This is an extension version of `example2.py`. It can search, extract, and record the data regarding a list of search values.


## How to run the code

You can run each Python file individually, for example:

1. `python3 json_lib.py`
2. `python3 example1.py`
3. `python3 example2.py`
4. `python3 example3.py`
   
Note: You need to have all the dependencies installed in your environment.

## Result

The output will be shown in the console and saved in the root folder as a CSV file:
- 'example1_single_file_output.csv' (for `example1.py`)
- 'example2_multiple_orcids_output.csv' (for `example2.py`)
- 'example3_multiple_orcids_multiple_values_output.csv' (for `example3.py`)

## Future Enhancement
Since this is a generic library, there are lots of ways to customize it and extend the functionality based on the specific requirements. Potential additions could be more utilities to handle JSON objects or modify the search operation to suit different needs.