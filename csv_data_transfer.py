import pandas as pd

def append_csv_data(source_file, destination_file):
    """
    Appends data from source CSV to destination CSV.

    Args:
        source_file (str): Path to the source CSV file.
        destination_file (str): Path to the destination CSV file where data should be appended.
    """
    try:
        # Read the source CSV file
        df = pd.read_csv(source_file)
        
        # Append the data to the destination CSV file
        df.to_csv(destination_file, mode='a', header=False, index=False)
        
        print(f"Data appended successfully from '{source_file}' to '{destination_file}'.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

append_csv_data('naukri_jobs_detailed_2025-07-05.csv', 'naukri_jobs_detailed_2025-07-02.csv')
