# UniConnect

UniConnect is a university group application developed as part of a Software Development Project course.  
The goal of the application is to facilitate communication and organization within university classes by providing a dedicated platform for students, class delegates, and professors.

The platform allows users to create and join class groups, exchange messages, publish official announcements, access class schedules, organize study events, and elect class delegates through an integrated voting system.  
By combining messaging features with academic-specific tools, the application aims to provide a structured and reliable alternative to generic chat applications for educational use.

The project focuses on collaborative software development, clean architecture, and the implementation of role-based access and real-world use cases.

---

## Features

- User authentication and role management (students, delegates, professors)
- Class-based group messaging
- Official announcements posted by professors and delegates
- Access to class schedules
- Creation and management of study events
- Delegate election system with integrated voting
- Role-based permissions and access control

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

---

## Project Structure
TODO

---

## Architecture Overview

The application follows a client-server architecture with a clear separation between frontend and backend.

- The **frontend** is a static web application built using vanilla web technologies and communicates with the backend through HTTP requests.
- The **backend** exposes a REST API responsible for authentication, business logic, and database access.
- The **database** stores users, classes, messages, events, schedules, and voting data.

This modular architecture ensures maintainability, scalability, and ease of collaboration within the development team.

More details can be found in the `docs/` directory.

---

## Installation & Setup

### Backend (UV)
1. Navigate to the `server/` directory
2. Run ``uv run uvicorn app.main:app --reload`` (You need to have ``uv`` installed, see [here](https://docs.astral.sh/uv/getting-started/installation/) for more)

### Backend (Nix)
1. Navigate to the `server/` directory
2. Run ``direnv allow``
2. Run ``uvicorn app.main:app --reload``

### Frontend
1. Navigate to the `website/` directory
2. Open `index.html` in a web browser
3. Ensure the backend server is running for full functionality

Detailed setup instructions will be provided in the documentation.

---

## Usage

- Users can register and log in to the platform
- Join or create class groups
- Communicate via group chats
- View announcements and schedules
- Organize or participate in study events
- Vote in delegate elections

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
