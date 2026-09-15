# Discord Employee Updates Bot

A Discord-based employee work update and validation system.

Employees can submit their work updates directly through Discord. Submissions are stored in PostgreSQL and displayed as Discord embeds in the designated submission channel.

Validators can review submissions, add suggestions, and independently validate them.

---

## Features

- Submit employee work updates through `/submit work`
- Restrict the bot to one designated Discord server
- Restrict submissions to one designated Discord channel
- Optional description, links, and attachment
- Store submissions in PostgreSQL
- Display submissions as Discord embeds
- Add suggestions to submissions
- Validator role-based permissions
- Prevent employees from validating their own submissions
- Support multiple validators for the same submission
- Prevent the same validator from validating a submission more than once
- Optional validation notes
- Track validation history
- SQLAlchemy ORM
- Alembic database migrations

---

## Tech Stack

- Python
- discord.py
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic Settings

---

## Architecture

The project follows a layered architecture:

```text
Discord
   │
   ▼
discord.py Bot
   │
   ▼
Commands / Views / Modals
   │
   ▼
Application Service Layer
   │
   ▼
SQLAlchemy ORM
   │
   ▼
PostgreSQL
```

### Project Structure

```text
discord_server/
│
├── app/
│   └── services/
│       └── submission_service.py
│
├── bot/
│   ├── main.py
│   │
│   ├── commands/
│   │   └── submission.py
│   │
│   └── views/
│       ├── submission_view.py
│       ├── suggestion_modal.py
│       └── validation_modal.py
│
├── config/
│   ├── database.py
│   └── settings.py
│
├── models/
│   ├── base.py
│   ├── submission.py
│   └── submission_validation.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/karanyogix/Discord.git
cd Discord
```

---

## 2. Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# PostgreSQL Setup

The project uses PostgreSQL as its database.

Create a PostgreSQL database named:

```text
employee_updated
```

The default PostgreSQL port is:

```text
5432
```

You will need:

- PostgreSQL username
- PostgreSQL password
- PostgreSQL database name
- PostgreSQL host
- PostgreSQL port

---

# Environment Variables

Create a `.env` file in the project root:

```text
discord_server/
│
├── .env
├── bot/
├── app/
└── ...
```

Add the following configuration:

```env
# Discord configuration
DISCORD_BOT_TOKEN=your_discord_bot_token

# Database configuration
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/employee_updated

# Validator role configuration
VALIDATOR_ROLE_ID=123456789012345678

# Company Discord server and submission channel
TARGET_GUILD_ID=123456789012345678
SUBMISSION_CHANNEL_ID=987654321098765432
```

Replace the placeholder values with your actual configuration.

### Environment Variable Descriptions

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Token for the Discord bot |
| `DATABASE_URL` | PostgreSQL connection URL |
| `VALIDATOR_ROLE_ID` | Discord role ID for validators |
| `TARGET_GUILD_ID` | ID of the company Discord server |
| `SUBMISSION_CHANNEL_ID` | ID of the designated work submission channel |

### How to Get Discord IDs

Enable Developer Mode in Discord:

1. Open Discord User Settings.
2. Go to **Advanced**.
3. Enable **Developer Mode**.

Then:

- Right-click the company server and select **Copy Server ID**.
- Right-click the submission channel and select **Copy Channel ID**.

### Important

Never commit `.env` to Git.

The repository's `.gitignore` should exclude it.

You can use `.env.example` as a template without including real secrets.

If your PostgreSQL password contains special characters such as `@`, URL-encode the character.

For example:

```text
Original password:
my@password
```

Becomes:

```text
my%40password
```

Inside the database URL:

```env
DATABASE_URL=postgresql+psycopg://postgres:my%40password@localhost:5432/employee_updated
```

---

# Discord Bot Setup

Create a Discord application and bot through the Discord Developer Portal.

The bot must be invited to the company Discord server with the required permissions:

- View Channels
- Send Messages
- Read Message History
- Embed Links
- Attach Files
- Use Application Commands

The bot also uses a Discord role named:

```text
Validator
```

Members with this role can validate other employees' submissions.

## Server and Channel Restrictions

The bot is configured to work with:

1. One specific Discord server.
2. One specific submission channel inside that server.

The `/submit work` command is rejected when it is used:

- In a direct message.
- In another Discord server.
- In a channel other than the configured submission channel.

These restrictions are controlled by:

```env
TARGET_GUILD_ID=your_company_server_id
SUBMISSION_CHANNEL_ID=your_submission_channel_id
```

---

# Database Migrations

This project uses Alembic to manage database schema changes.

After configuring PostgreSQL and `.env`, run:

```powershell
alembic upgrade head
```

This applies all migrations to the database.

Check the current migration:

```powershell
alembic current
```

---

## Creating a New Migration

After changing a SQLAlchemy model:

```powershell
alembic revision --autogenerate -m "describe your change"
```

Review the generated migration before applying it.

Apply the migration:

```powershell
alembic upgrade head
```

### Important

Do not use `create_tables.py` for schema evolution.

Alembic should be used for database migrations.

---

# Running the Bot

From the project root:

```powershell
python -m bot.main
```

You should see output similar to:

```text
Logged in as YourBot
Slash commands synced.
```

---

# Using the Bot

## Submit a Work Update

Employees use:

```text
/submit work
```

The command accepts:

- `title` — required
- `description` — optional
- `links` — optional
- `attachment` — optional

The command must be used in the configured submission channel.

The submission is posted in the same channel where the command was used.

---

# Submission Workflow

```text
Employee
   │
   │ /submit work
   ▼
Discord Bot
   │
   ├── Check server ID
   │
   ├── Check channel ID
   │
   ├── Save submission
   │
   ├── Create Discord embed
   │
   └── Post submission
   │
   ▼
🟡 Pending Validation
```

The submission contains an:

```text
⚙️ Open Actions
```

button.

---

# Suggestions

Any employee can open the actions panel and choose:

```text
💡 Add Suggestion
```

The suggestion is posted as a Discord reply to the original submission.

This keeps suggestions associated with the submission.

Users can only edit or delete their own suggestions.

---

# Validation

Users with the `Validator` role can validate another employee's submission.

The validator sees:

```text
💡 Add Suggestion
✅ Validate Submission
```

The validation note is optional.

A validator cannot validate their own submission.

---

## Multiple Validators

A submission can be validated by multiple validators.

For example:

```text
Submission #12

Validations:

👤 Validator A
   Looks good.

👤 Validator B
   Completed from my side.
```

Each validator provides their own independent validation.

The same validator cannot validate the same submission twice.

Once at least one validation exists, the submission status becomes:

```text
🟢 Validated
```

Other eligible validators can still validate the submission.

---

# Database Model

The main database tables are:

```text
submissions
    │
    │ one-to-many
    ▼
submission_validations
```

### `submissions`

Stores the main employee work update.

Examples of stored information:

- Title
- Description
- Links
- Attachment URL
- Employee Discord ID
- Submission timestamp
- Discord channel ID
- Discord message ID
- Validation status

### `submission_validations`

Stores individual validator records.

Examples:

- Submission ID
- Validator Discord ID
- Validation note
- Validation timestamp

A unique constraint prevents the same validator from validating the same submission more than once.

---

# Security

The bot performs permission and ownership checks in the application logic.

For example:

- Only users with the `Validator` role can validate.
- Employees cannot validate their own submissions.
- A validator cannot validate the same submission twice.
- Suggestions are associated with the original submission.
- Users can only edit or delete their own suggestions.
- The bot checks the configured Discord server ID.
- The bot checks the configured submission channel ID.

UI restrictions are not treated as the only security mechanism.

Validation and ownership rules are also checked when the action is actually processed.

---

# Development Workflow

When developing a new feature:

```text
1. Change the code
       ↓
2. Test locally
       ↓
3. If database models changed,
   create an Alembic migration
       ↓
4. Run the migration
       ↓
5. Test the bot
       ↓
6. Commit the changes
       ↓
7. Push to GitHub
```

Example:

```powershell
git status

git add .

git commit -m "Add new feature"

git push
```

---

# Current Version

The current version provides the initial employee work submission and validation workflow through Discord.

It includes:

- Employee work submissions
- PostgreSQL persistence
- Discord embed messages
- Suggestions
- Role-based validation
- Multiple validators
- Validation history
- Server and channel restrictions

Future versions can extend the system with features such as:

- More attachment handling
- Comment persistence in PostgreSQL
- Employee management
- Reporting and analytics
- Admin commands
- Web dashboard
- Authentication
- Advanced validation workflows
- Automated reports

---

## License

This project is currently intended for development and internal use.