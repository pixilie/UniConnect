# UniConnect

UniConnect is a university group application developed as part of a Software Development Project course.  
The goal of the application is to facilitate communication and organization within university classes by providing a dedicated platform for students, class delegates, and professors.

The platform allows users to create and join class groups, exchange real-time messages, publish official announcements, access class schedules, organize study events, and elect class delegates through an integrated voting system.  
By combining messaging features with academic-specific tools, the application aims to provide a structured, secure, and reliable alternative to generic chat applications for educational use.

---

## 🚀 Features

- **User Authentication:** Secure login with role management (Students, Delegates, Professors) via JWT.
- **Real-Time Chat:** Class-based group messaging powered by WebSockets.
- **Official Announcements:** Priority dashboard posts by professors and delegates.
- **Interactive Timetables:** Access to class schedules (parsed from `.ics` files) and dynamic study events.
- **Election System:** Interactive polling system to elect class delegates with real-time results.
- **Resource Sharing:** File uploading system allowing teachers to share course-related documents easily.
- **Role-Based Permissions:** Strict access control for administrative and teaching actions.

---

## 🛠️ Tech Stack

### Frontend
- **HTML5 & CSS3** (Custom styling, responsive design)
- **Vanilla JavaScript** (DOM manipulation, native State Management, no heavy frameworks)
- **WebSockets** (Real-time bidirectional communication)

### Backend
- **Python 3**
- **FastAPI** (High-performance REST API and WebSocket routing)
- **SQLAlchemy ORM** (Database management)
- **Uvicorn** (ASGI web server)

### Infrastructure & Database
- **SQLite / PostgreSQL** (Relational data storage)
- **Docker & Docker Compose** (Containerization and deployment)
- **Caddy** (Reverse Proxy & automatic HTTPS)
- **pgAdmin** (Database administration)

---

## 🏗️ Architecture Overview

The application follows a strict Client-Server architecture with a clear separation of concerns:

- The **Frontend** is a lightweight Single Page Application (SPA) built natively. It communicates with the backend through REST HTTP requests for data fetching and WebSockets for real-time chat.
- The **Backend** exposes a modularized FastAPI application responsible for authentication, business logic, and database transactions.
- The **Database** stores users, classes, messages, announcements, events, schedules, and voting data following a normalized entity-relationship model.

This modular architecture ensures maintainability, scalability, and zero-dependency frontend operation, perfectly aligning with our academic requirements. More details can be found in the `docs/` directory.

---

## 💻 Installation & Setup

### Option 1: Local Development (UV)

1. Clone the repository and navigate to the project directory.
2. Run `uv sync` to install dependencies. *(You need to have [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, or type `direnv allow` if you're using Nix).*
3. Start the development server:
   ```bash
   uv run uvicorn app.main:app --reload
