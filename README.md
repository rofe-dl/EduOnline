# EduOnline
EduOnline is a platform for teachers and students to give MCQ based exams. Teachers can login with an admin account, make their own subjects, and create timed exams for it. Students can then login with their accounts and attend the exam. Their results are then automatically graded and displayed to the teacher upon request.

## Setup Instructions
1. Install MariaDB and the required development libraries for it
    ```
    // Development libraries
    sudo apt install libmariadb-dev libmariadb-dev-compat libmariadbclient-dev
    sudo apt install python3-dev
    ```
1. Create a database called `eduonline` in MariaDB
1. In the `EduOnline` directory, make a `secrets.py` file and write down the secret variables required
    ```
    DJANGO_SECRET_KEY = '<any random string>'
    DATABASE_PASSWORD = '<your mariadb database password>'
    ```
    Then in the `local_settings.py` file, search for `DATABASES` and change the username there to the username of your database (usually `root`)
1. Make a virtual environment of python and install dependencies
    ```
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```
1. Create an admin user for the Django project

    `python3 manage.py createsuperuser --settings=EduOnline.local_settings`

1. Migrate the changes to your database.

    ```
    python3 manage.py makemigrations --settings=EduOnline.local_settings
    python3 manage.py migrate --settings=EduOnline.local_settings
    ```
1. Run the server with the local settings.

    `python3 manage.py runserver --settings=EduOnline.local_settings`

## Development
* Python 3
* Django
* MariaDB
* jQuery
* JavaScript
* Bootstrap 