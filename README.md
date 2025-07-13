# Epic Events CRM (Command-Line Application)

A command-line CRM built for **Epic Events** to manage clients, contracts and events.  
Designed with role-based permissions for the commercial, support and management teams.

## Technology

- Python ≥ 3.11
- Poetry for dependency management
- SQLite via SQLAlchemy ORM
- Menu-driven interface built with custom view system
- Sentry SDK for logging

## Setup

1. **Clone and install**

   ```bash
   git clone https://github.com/Ju-l-e-s/crm_cli.git
   cd crm_cli
   poetry shell
   poetry install
   ```

2. **Environment Configuration**

   Create a `.env` file in the root directory with the following variables:

   ```env
   # JWT Configuration
   JWT_SECRET=your_jwt_secret_key_here
   JWT_EXPIRES_IN=86400  # Token expiration time in seconds (24 hours)

   # Sentry Configuration (for error tracking)
   SENTRY_DSN=your_sentry_dsn_here
   DISABLE_SENTRY=1  # Set to 1 to disable Sentry

   # Application Environment
   APP_ENV=dev
   ```

3. **Set up the database**

   ```bash
   poetry run python database/create_db.py
   poetry run python seed.py
   ```

4. **Run the application**
   ```bash
   poetry run python main.py
   ```

## Test Data & Credentials

The database is populated with sample data using the seed script. It contains 6 users (2 of each role), 2 clients, 2 contracts, and 2 events.

### Test User Credentials

| Role       | Email           | Password      |
| ---------- | --------------- | ------------- |
| Commercial | lisa@test.com   | Azertyuiop123 |
| Commercial | marge@test.com  | Azertyuiop123 |
| Management | homer@test.com  | Azertyuiop123 |
| Management | abram@test.com  | Azertyuiop123 |
| Support    | bart@test.com   | Azertyuiop123 |
| Support    | maggie@test.com | Azertyuiop123 |

## Usage

1. Start the application:
   ```bash
   poetry run python main.py
   ```
2. Follow the menus to navigate through the application
3. Main menu options include:

   - Authentication (login/logout)
   - Client management
   - Contract management
   - Event management
   - User management (management role only)

   The interface is intuitive and will guide you through each operation with clear prompts.

## Roles & Permissions

| Role       | Clients   | Contracts | Events         | Users |
| ---------- | --------- | --------- | -------------- | ----- |
| Management | R/W/D     | R/W       | R/W            | R/W/D |
| Commercial | R/W (own) | R/W (own) | Create (own)   | R     |
| Support    | R         | R         | R/W (assigned) | R     |

_R = read, W = write, D = delete_

## Project Structure

```
crm_cli/
│
├── config/                        # Application configuration
│   ├── console.py                # Custom console interface settings
│   └── sentry_logging.py         # Error tracking configuration
│
├── controllers/                   # Business logic
│   ├── repositories/             # Data access layer
│   │   ├── client_repository.py
│   │   ├── contract_repository.py
│   │   ├── event_repository.py
│   │   └── user_repository.py
│   │
│   ├── services/                 # Business services
│   │   ├── auth.py
│   │   ├── authorization.py
│   │   └── token_cache.py
│   │
│   ├── validators/               # Input validation
│   │   └── validators.py
│   │
│   ├── auth_controller.py
│   ├── client_controller.py
│   ├── contract_controller.py
│   ├── event_controller.py
│   ├── menu_controller.py
│   └── user_controller.py
│
├── database/  # Database files
│   ├── create_db.py 
│   ├── session.py                   
│   └── test.db
│
├── models/                       # Data models
│   ├── base.py
│   ├── client.py
│   ├── contract.py
│   ├── event.py
│   └── user.py
│
├── tests/
│   ├── integration/              # Integration tests
│   └── unit/                     # Unit tests
│
├── views/                        # CLI interfaces
│   ├── auth_view.py
│   ├── base.py
│   ├── client_view.py
│   ├── contract_view.py
│   ├── event_view.py
│   ├── menu_view.py
│   └── user_view.py
│
├── .env                         # Environment variables
├── .gitignore
├── README.md
├── main.py                     # Application entry point
├── poetry.lock
├── pyproject.toml             # Dependencies
└── requirements.txt
```

## Security Notes

- ORM queries protect against SQL injection.
- Only required privileges are granted to each role.
- Passwords are stored hashed (argon2).

## Logging & Monitoring

All exceptions are captured and sent to Sentry when `SENTRY_DSN` is activated.