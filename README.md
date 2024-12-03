# Klasstra

**Klasstra** is a web application designed to streamline communication and collaboration in classroom communities. It provides a central platform for teachers, parents, and potentially students to share announcements, updates, and more. While initially built for the teachers in my son's class, Klasstra is designed to be flexible and scalable, accommodating a wide range of educational use cases in the future.

## Features

- **Announcements:** Teachers can easily post updates and announcements.
- **Communication:** A simplified channel for teachers to communicate with parents.
- **Scalability:** Built with the potential to expand into broader educational tools.

## Motivation

Klasstra was born out of a personal need to bridge communication gaps in my son's classroom. Currently, teachers rely on paper and email for announcements, which can be inefficient and scattered. This project aims to centralize these communications and make them more accessible and organized.

## Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) - A modern, fast (high-performance) web framework for Python.
- **Database:** PostgreSQL - A powerful, open-source object-relational database system.
- **Frontend:** Basic HTML and CSS (No external frameworks like Bootstrap).
- **Templating:** Jinja2 for creating reusable and dynamic components.

## Installation

Follow these steps to set up Klasstra on your local machine:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/klasstra.git
   cd klasstra


2. Set up a virtual environment:
python3 -m venv env
source env/bin/activate  # For Windows: .\env\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Configure the database:
Ensure you have PostgreSQL installed.
Create a database named klasstra_db.
Update the DATABASE_URL in database.py to match your setup.

5. Run database migrations:
alembic upgrade head

6. Start the FastAPI server:
uvicorn app.main:app --reload
Access the app: Open your browser and go to http://localhost:8000.

## Usage

Current Capabilities:
Create, Read, Update, and Delete (CRUD) Todos for testing functionality.
Post and view announcements.
Future features under exploration: Scheduling, event management, and parent-teacher interactions.

Planned Enhancements:
Role-based access (teachers, parents, admin).
Multilingual support for international users (German, French, and English).
Improved frontend design with modular components.

Lessons Learned
This project is my first un-guided coding experience after learning Python and FastAPI through courses and personal practice. It's been a rewarding challenge to move from structured tutorials to self-reliant development.

## Acknowledgments
Angela Yu's Udemy Course: A fantastic resource that kickstarted my Python journey.
ChatGPT: My ever-patient coding assistant.
Teachers everywhere for inspiring this app with their dedication.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
Linkedin: https://www.linkedin.com/in/ivkoberg/

Author: Ivan Berg
Klasstra – Connecting classrooms, one update at a time!