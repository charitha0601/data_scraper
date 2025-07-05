import pandas as pd

def check_and_remove_duplicates(file_path):
    """
    Checks for duplicate rows in a CSV file and removes them if found.

    Args:
        file_path (str): Path to the CSV file.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Check for duplicates
        duplicate_rows = df[df.duplicated()]
        duplicate_count = len(duplicate_rows)

        if duplicate_count > 0:
            print(f"Found {duplicate_count} duplicate row(s):")
            print(duplicate_rows)

            # Remove duplicates
            df_cleaned = df.drop_duplicates()
            df_cleaned.to_csv(file_path, index=False)
            print("Duplicates removed successfully.")
        else:
            print("No duplicate rows found. File is clean.")

    except Exception as e:
        print(f"An error occurred: {e}")

check_and_remove_duplicates('naukri_jobs_detailed.csv')
