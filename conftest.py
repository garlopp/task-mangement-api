import sys
import os

# Add the project root directory to the Python path
# This ensures that modules like 'models', 'schemas', etc., can be imported directly
# from any test file, regardless of its location within the project.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)