import os

reject_list = ['venv', "__pycache_", ".vscode", ".git"]

def print_folder_contents(folder_path, indent_level=0):
    try:
        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"The folder does not exist.")
            return
        
        # Get the list of files and directories in the folder
        items = os.listdir(folder_path)
        
        if not items:
            print(f"{' ' * indent_level}The folder is empty.")
        else:
            for item in items:
                item_path = os.path.join(folder_path, item)

                # Skip items that match the reject list
                if any(reject in item for reject in reject_list):
                    continue

                if os.path.isdir(item_path):
                    print(f"{' ' * indent_level}[DIR]  {item}")
                    # Recursively print the contents of the subdirectory
                    print_folder_contents(item_path, indent_level + 4)  # Increase indentation for subfolders
                else:
                    print(f"{' ' * indent_level}[FILE] {item}")

    except Exception as e:
        print(f"An error occurred while processing {folder_path}: {e}")

if __name__ == "__main__":
    # Fetch the current directory
    current_dir = os.getcwd()
    # Get the parent directory by removing the last part of the path
    parent_dir = os.path.dirname(current_dir)
    
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    
    # Print the contents of the parent directory
    print_folder_contents(parent_dir)