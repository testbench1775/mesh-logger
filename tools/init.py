# Script to overwrite xxx.py

# Cpanels python program interface overwrites this file every once in a while
# Not sure why, but run this when it does. You will rx a 500 error.
file_path = '../passenger_wsgi.py'

content = """import sys
sys.path.insert(0, '/repositories/mesh-logger/interface')
from app import app as application
"""

with open(file_path, 'w') as file:
    file.write(content)

print(f"{file_path} has been successfully overwritten.")

