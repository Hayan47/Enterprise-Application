# Source Safe

A platform that let users share and edit files organized in groups regarding Concurrent Access.

## Prerequisites

- Python 3.x
- Node.js
- Redis (for automatic tasks)

## Installation

1. Clone the repository:
   `git clone https://github.com/Hayan47/Enterprise-Application.git`


2. Navigate to the project directory:
  `cd yourprojectname`


3. Install Python dependencies:
  `pip install -r requirements.txt`


4. Install Node.js dependencies (including Tailwind CSS):
  `npm install`


## Running the Project

- Run the Django server:
  `python manage.py runserver`

- Run Celery (Task queue):
  `celery -A files_test worker --pool=solo -l info -E`
  `celery -A files_test beat -l info`


