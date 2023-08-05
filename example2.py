import re
import json
import requests
from json_lib import * # Import the functions from the json_lib.py file

##Example 1
# Search  for a keyword in a single ORCID


# Define the search value and keys to search for
search_value = 'Chan Zuckerberg Initiative, Redwood City, California, USA' # this is the value that we want to search for in the json file
keys_to_search = ['title', 'doi', 'type']# this is the list of keys that we want to extract from the json file
orcid='0000-0003-0232-2196' # this is the name of the json file that we want to extract the data from







    

def construct_table_with_keys(json_obj: dict, search_value: str, keys_to_search: List[str], orcid: str) -> pd.DataFrame:
    """
    Constructs a table with the specified keys and the value that was searched for in the JSON object.
    The function searches for the specified value in the JSON object and then searches for each key in the
    list of keys to search for at all levels relative to the path leading to the value. If all keys are found,
    the function adds the row to the table data. The resulting table is returned as a pandas DataFrame.

    Args:
        json_obj (dict): The JSON object to search for the specified value and keys.
        search_value (str): The value to search for in the JSON object.
        keys_to_search (List[str]): The list of keys to search for at all levels relative to the path leading
            to the value.
        orcid (str): The value to be added as the first column of the resulting DataFrame.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the extracted data.

    Example:
        ...

        >>> orcid_value = "0000-0001-1234-5678"
        >>> construct_table_with_keys(json_obj, search_value, keys_to_search, orcid_value)
            orcid     values      name    type
        0  0000-0001-1234-5678  Mittens  Mittens     cat
    """
    # Find all paths leading to the specified value using the find_all_paths_of_value function
    paths_to_search_value = list(find_all_paths_of_value(search_value, json_obj))

    # List to store the extracted table data
    table_data_all_levels = []

    # Set to track unique rows and exclude duplicates
    unique_rows = set()

    # Iterate through each path found and use search_key_in_all_levels to find the specified keys
    for path in paths_to_search_value:
        row_data = [orcid, search_value] # Include orcid value as the first item in the row
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

    # Define columns for the DataFrame, including the orcid and specified keys
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

#Lets extract the data from one of the json files and save the results as a csv file

# Define the search value and keys to search for
search_value = 'Chan Zuckerberg Initiative, Redwood City, California, USA' # this is the value that we want to search for in the json file
keys_to_search = ['title', 'doi', 'type']# this is the list of keys that we want to extract from the json file
file='0000_0003_0232_2196.json' # this is the name of the json file that we want to extract the data from


# Open the JSON file and save it as a dictionary
with open(file, 'r') as f:
    data = json.load(f)


# Call the construct_table_with_keys function to get a pandas DataFrame 
#see the function definition above to learn how it works
table_df = construct_table_with_keys(data, search_value, keys_to_search, file)
# Print the pandas DataFrame
print(table_df)
#save the dataframe as a csv file
table_df.to_csv('single_file_output.csv', index=False)





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