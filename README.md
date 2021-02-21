Eagle Financial Services:

The application Eagle Financial System is designed to manage the recipient customers, stocks and investments of customers.

Local Installation Steps
Please find the below steps to run the application locally. Assuming git cli software is installed in the local machine.

Pull application from GitHub url to your project folder for example say “PythonProjects” folder: https://github.com/Santhosh417/efs.git
      git clone https://github.com/Santhosh417/efs.git
Create virtual environment. Ex: “venv” folder
    python -m virtualenv venv
Go to venv/bin and activate virtual environment
      cd venv/bin
      source activate
Go to project root folder where manage.py file is preset. Go to “bloodbankms” folder.
    cd ../../
Install required dependencies in virtual environment as mention in “requirements.txt” file with below command
    pip  install -r requirements.txt
Install tables in venv
    python manage.py makemigrations
    python manage.py migrate
create super user
    python manage.py createsuperuser
Run server
   Python manage.py runserver
Open http://127.0.0.1:8000/ on browser and you should see application landing page.
Yay!! Application local setup is successful.

NOTE:
WeasyPrint dependency is used for PDF generation. If running locally and facing, issues with easy print, install WeasyPrint using
https://weasyprint.readthedocs.io/en/stable/install.html


