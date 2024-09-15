# Script to overwrite xxx.py

file_path = 'xxx.py'  # Path to the file you want to overwrite

content = """import sys

# Add your project directory to the sys.path
sys.path.insert(0, '/repositories/mesh-logger/interface')

# Import your application module
from app import app as application
"""

# Write the content to the file
with open(file_path, 'w') as file:
    file.write(content)

print(f"{file_path} has been successfully overwritten.")

