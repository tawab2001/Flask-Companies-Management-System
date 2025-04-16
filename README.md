# Flask Companies Management System

A simple Flask web application for managing company information with CRUD operations.

## Features

- List all companies
- View detailed company information
- Add new companies
- SQLite database integration
- Form validation
- Responsive design

## Technologies Used

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-WTF
- SQLite

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd flask-companies
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install flask flask-sqlalchemy flask-migrate flask-wtf
```

4. Initialize the database:
```bash
set FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Running the Application

1. Set environment variables:
```bash
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1
```

2. Run the application:
```bash
flask run
```

3. Open your browser and navigate to `http://127.0.0.1:5000/companies`

## Project Structure

```
flask-companies/
├── app.py                  # Main application file
├── companies.db           # SQLite database
├── migrations/           # Database migrations
├── templates/           # HTML templates
│   ├── companies.html    # Companies list template
│   ├── company_detail.html # Company detail template
│   └── company_form.html  # Company creation form
└── README.md            # Project documentation
```

## API Routes

- `GET /companies` - List all companies
- `GET /company/<id>` - View specific company details
- `GET /company/create` - Display company creation form
- `POST /company/create` - Handle company creation

## Database Schema

### Company
- id (Integer, Primary Key)
- name (String, 100 characters)
- description (Text)
- employees_count (Integer)
- location (String, 100 characters)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
