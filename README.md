# UniConnect

UniConnect is a university group application developed as part of a Software Development Project course.  
The goal of the application is to facilitate communication and organization within university classes by providing a dedicated platform for students, class delegates, and professors.

The platform allows users to create and join class groups, exchange messages, publish official announcements, access class schedules, organize study events, and elect class delegates through an integrated voting system.  
By combining messaging features with academic-specific tools, the application aims to provide a structured and reliable alternative to generic chat applications for educational use.

---

## Features

- User authentication and role management (students, delegates, professors)
- Class-based group messaging
- Official announcements posted by professors and delegates
- Access to class schedules
- Creation and management of study events / fun activities
- Polls system
- Role-based permissions and access control
- Ressources uploding system so teacher can share course related documents easily

---

## Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- RESTful API
- SQL database (SQLite / PostgreSQL)

### Tools
- Git & GitHub
- Markdown documentation
- Trello

---

## Architecture Overview

The application follows a client-server architecture with a clear separation between frontend and backend.

- The **frontend** is a static web application built using vanilla web technologies and communicates with the backend through HTTP requests.
- The **backend** exposes a REST API responsible for authentication, business logic, and database access.
- The **database** stores users, classes, messages, annoucements, events, schedules, and voting data.

This modular architecture ensures maintainability, scalability, and ease of collaboration within the development team.
More details can be found in the `docs/` directory.

---

## Installation & Setup

### Installation (UV)
1. Navigate to the `server/` directory
2. Run ``uv sync`` (You need to have ``uv`` installed, see [here](https://docs.astral.sh/uv/getting-started/installation/) for more or type `direnv allow` if you're using Nix)

### Running
1. Navigate to the project directory
2. Run ``uv run uvicorn app.main:app --reload`` and open the url ``127.0.0.1:8000`` in your browser.

---

## Documentation

Additional documentation is available in the `docs/` directory:
- Architecture overview
- Functional requirements
- Use cases
- Development guidelines

---

## Contributing

This project is developed as part of a university course and follows a collaborative workflow.

Basic contribution guidelines:
- Create a feature branch from `main`
- Commit clear and descriptive messages
- Open a pull request for review
- Respect the existing architecture and coding standards

---

## License

This project is licensed under the MIT License.
