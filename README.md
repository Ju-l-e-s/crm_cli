# Epic Events CRM (Command-Line Application)

A command-line CRM built for **Epic Events** to manage clients, contracts and events.  
Designed with role-based permissions for the commercial, support and management teams.


## Technology

- Python ≥ 3.9
- Poetry for dependency management
- SQLite (default) via SQLAlchemy ORM – easy switch to other RDBMS
- Menu-driven interface built with custom view system
- Sentry SDK for logging

## Setup

1. **Clone and install**

   ```bash
   git clone https://github.com/Ju-l-e-s/crm_cli.git
   poetry install
   ```

2. **Set up the database**

   ```bash
   poetry run python database/create_db.py
   poetry run python seed.py
   ```

3. **Run the application**
   ```bash
   poetry run python main.py
   ```

## Usage

1. Start the application:
   ```bash
   poetry run python main.py
   ```
2. Follow the on-screen menus to navigate through the application
3. Main menu options include:

   - Authentication (login/logout)
   - Client management
   - Contract management
   - Event management
   - User management (management role only)

   The interface is intuitive and will guide you through each operation with clear prompts.

## Roles & Permissions (Least Privilege)

| Role       | Clients   | Contracts | Events         | Users |
| ---------- | --------- | --------- | -------------- | ----- |
| Management | R/W/D     | R/W       | R/W            | R/W/D |
| Commercial | R/W (own) | R/W (own) | Create (own)   | R     |
| Support    | R         | R         | R/W (assigned) | R     |

_R = read, W = write, D = delete_

## Security Notes

- ORM queries protect against SQL injection.
- Only required privileges are granted to each role.
- Passwords are stored hashed (argon2).

## Logging & Monitoring

All exceptions are captured and sent to Sentry when `SENTRY_DSN` is activated.