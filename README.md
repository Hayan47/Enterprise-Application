# Source Safe

A platform that allows users to share and edit files organized in groups, focusing on concurrent access.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed on your system:

- [Python 3.x](https://www.python.org/downloads/)
- [Redis](https://redis.io/download) (for automatic tasks)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Hayan47/Enterprise-Application.git
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Redis:**
   Download and install Redis from [this link](https://github.com/tporadowski/redis/releases).
   Choose version 5.0.10.

## Running the Project

Follow these steps to run the Source Safe project:

- **Run the Django server:**

  ```bash
  python manage.py runserver
  ```

- **Run Celery (Task queue):**
  ```bash
  celery -A source_safe worker --pool=solo -l info -E
  celery -A source_safe beat -l info
  ```
