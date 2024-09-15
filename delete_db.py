import os

def delete_db_file(db_file='nodeData.db'):
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"{db_file} has been deleted successfully.")
        else:
            print(f"{db_file} does not exist.")
    except Exception as e:
        print(f"Error occurred while deleting the file: {e}")

if __name__ == "__main__":
    delete_db_file()