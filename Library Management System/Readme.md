## Library Management System - Flask App

This is a Flask application for managing ebooks in a library.

### Prerequisites

* Python 3.x ([https://www.python.org/downloads/](https://www.python.org/downloads/))
* pip (usually comes bundled with Python)

### Installation

1. Clone this repository or download the zip file.
2. Create a virtual environment (recommended for managing dependencies):

```bash
python -m venv venv
source venv/bin/activate  # activate for Linux/macOS
venv\Scripts\activate.bat  # activate for Windows
```

3. Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

This will start the Flask development server, usually accessible at http://127.0.0.1:5000/ (port might vary).

**Note:** This is a basic setup and doesn't include any configuration for a production environment.


### Usage

The application provides functionalities for both Librarians and Users (login required):

* **Librarians:**
    * Manage ebooks (add, edit, remove)
    * Manage sections
    * Assign ebooks to sections
    * Track borrowed ebooks
    * View user requests
* **Users:**
    * Browse ebooks
    * Search ebooks by section or author
    * Request ebooks
    * See borrowed ebooks

**Note:** Login functionality for admin is currently implemented with a simple username/password form. Security features are not implemented in this version. While for user the authentication is available.


### Project Structure

The project is organized with the following folders:

* `applicaion`: Contains the core application logic (views, models, etc.)
* `templates`: Contains HTML templates for rendering pages.
* `db_directory`: Contains the db.sqlite file used as SQLite database.
* `requirements.txt`: Lists the required Python libraries.
* `app.py`: The entry point to run the Flask application.


### Contributing

Feel free to fork the repository and contribute with improvements or new features.
