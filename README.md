# FLASK BOOKLIST

This project is a Flask-based web application that explores JWT authentication and middlewares. The backend handles user authentication, enforcing secure login/logout mechanisms, and applying middleware for request validation and logging. This setup provides a structured way to learn about jwt based authentication, middleware functions, and nosql database in a Flask environment.

## TechStack

- Flask
- Tailwindcss
- Mongodb

## Installation

### Prerequisites

- Python 3.11+
- pip (Python package installer)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/blueorionn/Flask-BookList.git
   cd Flask-BookList
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Export variables:

   ```bash
   export PYTHONDONTWRITEBYTECODE=1
   export FLASK_ENV="development"
   export SECRET_KEY="your-secret-key"
   export DB_HOST="your-database-host"
   export DB_NAME="your-database-name"
   export DB_USERNAME="your-database-username"
   export DB_PASSWORD="your-database-password"
   export DB_PORT="your-database-port"
   ```

5. Run the Flask app:

   ```bash
   python wsgi.py
   ```

6. Open the app in your browser at `http://127.0.0.1:8000/`.

## License

This project is released under the MIT License.
