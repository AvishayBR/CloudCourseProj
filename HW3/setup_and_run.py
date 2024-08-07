# setup_and_run.py

import os

# Change directory to the cloned repository
os.chdir('CloudCourseProj')
os.chdir('HW3')

# Install the required packages
os.system('pip install -r requirements.txt')

# Run the application
os.system('python app.py')