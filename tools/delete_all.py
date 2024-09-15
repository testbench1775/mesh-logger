import os
import shutil
import sys

def delete_all_including_self():
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script directory
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))  # Get the parent directory
    
    try:
        # Delete current directory content
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if item_path != os.path.abspath(__file__):  # Prevent deletion of the script until the end
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

        # Delete parent directory content
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if item != os.path.basename(current_dir):  # Prevent deletion of current directory prematurely
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
        
        # Delete the script itself
        os.remove(os.path.abspath(__file__))

    except Exception as e:
        print(f"Error occurred while deleting files: {e}")

if __name__ == "__main__":
    delete_all_including_self()