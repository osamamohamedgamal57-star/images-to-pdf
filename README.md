# Images to PDF - Telegram Bot

A Telegram bot that turns your photos into a single PDF file with the name you choose. Send it your images, type `/pdf`, tell it what to call the file, and get the PDF back in seconds. It also includes user statistics and a full admin panel inside Telegram, so the bot can be managed without touching the code.

The bot runs on your own computer: double-click one file (`run_bot.bat`) and it starts. No hosting, no server and no paid service are needed.

<!-- To add screenshots: create a folder named screenshots in this repo, upload your images there, then replace this line with:
![Creating a PDF](screenshots/create-pdf.png)
![Admin panel](screenshots/admin-panel.png) -->

## Why I built it

I wanted a project that goes beyond a web page: a real application that other people can use from their phones, with a database, an admin side and proper error handling. A bot that converts photos to PDF solves a problem I actually have (sending several photos as one document), and it let me practise the skills of a complete back-end project: handling asynchronous events, storing data in a database, separating the code into modules, protecting secrets, and writing automated tests.

## Features

**For users**
- Send normal photos or images sent as files (one by one or as an album)
- **Choose the name of the PDF**: after you type `/pdf`, the bot asks what to call the file (or type `/skip` for the default name)
- One PDF page per image, in the same order you sent them
- Photos that were taken sideways are rotated correctly (EXIF orientation)
- Images with transparency (like PNG) are converted safely
- Arabic and other languages are supported in file names
- Your images are deleted from the computer right after the PDF is sent

**For admins** (type `/admin` in Telegram)
- **Statistics:** total users, new users (today / 7 days / 30 days), active users (today / 7 days / 30 days), returning users, regular users, and PDFs created
- Edit the welcome message from Telegram, without touching the code
- Change the maximum number of images per PDF (1 to 100)
- The owner can add and remove other admins

**Reliability and safety**
- A file name typed by the user is cleaned first (characters that are not allowed in file names are removed, the length is limited, and `.pdf` is never doubled)
- If one of the files is not a valid image, the bot answers with a clear message instead of crashing
- A limit on the number of images per PDF protects the computer from huge uploads

## Commands

| Command | Who | What it does |
|---|---|---|
| `/start` | everyone | Shows the welcome message |
| `/pdf` | everyone | Asks for the PDF name, then creates and sends the file |
| `/skip` | everyone | Uses the default name (`images.pdf`) when the bot asks for a name |
| `/clear` | everyone | Deletes your images and starts over |
| `/cancel` | everyone | Cancels the question about the name (your images stay saved), or an admin edit |
| `/admin` | admins | Opens the admin panel |
| `/addadmin ID` | owner | Adds an admin |
| `/removeadmin ID` | owner | Removes an admin |

## How to use the bot

1. Open the bot in Telegram and type `/start`.
2. Send your photos. The bot confirms each one: "Image 1 saved".
3. Type `/pdf`.
4. When the bot asks "What should the PDF be called?", send a name, for example `Biology notes`. (Type `/skip` to use `images.pdf`.)
5. The bot sends you `Biology notes.pdf`.

## Built with

- **Python 3** for all the code
- **python-telegram-bot** (async version) to talk to Telegram
- **SQLite** (built into Python) for users, activity, PDFs, settings and admins
- **Pillow** to read the images and build the PDF
- **python-dotenv** to keep the secret token outside the code
- **unittest** for automated tests

## Run it yourself (Windows, step by step)

1. **Install Python** from [python.org](https://www.python.org/downloads/). During the installation, tick **"Add python.exe to PATH"**.
2. **Create your bot:** open [@BotFather](https://t.me/BotFather) in Telegram, send `/newbot`, follow the steps, and copy the token it gives you.
3. **Find your Telegram ID:** send any message to [@userinfobot](https://t.me/userinfobot) and copy the number it replies with. You will be the owner of the bot.
4. **Start the bot:** double-click `run_bot.bat`.
   - The first time, Notepad opens the `.env` file. Paste your token and your ID like this, save, and close Notepad:
     ```
     BOT_TOKEN=your-token-here
     ADMIN_ID=your-telegram-id
     ```
   - The script installs the required libraries automatically (only the first time).
5. When you see `Bot is running`, open your bot in Telegram and send `/start`.

The bot works only while the black window is open and the computer is connected to the internet. Close the window (or press `Ctrl+C`) to stop it.

**macOS / Linux:** create the `.env` file by copying `.env.example`, then run:
```bash
pip install -r requirements.txt
python bot.py
```

## Project structure

```
images-to-pdf-bot/
├── bot.py             # Telegram handlers and the main program
├── admin.py           # Admin panel: buttons, settings, admin management
├── db.py              # SQLite database: users, daily activity, PDFs, settings, admins
├── pdf_utils.py       # Converts images to a PDF and cleans the file name
├── test_db.py         # Unit tests for the database and the statistics
├── test_pdf_utils.py  # Unit tests for the PDF creation and the name cleaning
├── run_bot.bat        # Double-click launcher for Windows
├── requirements.txt   # Python libraries
├── .env.example       # Template for the secret settings
├── .gitignore         # Keeps secrets and the database out of GitHub
└── README.md          # Project description
```

## How it works

- The bot uses **polling**: the program asks Telegram every moment "is there a new message?" and answers it. Because of this, the bot needs no public web address and works from a normal home computer.
- Every incoming message first passes through a tracking handler that saves the user and marks them as active today. This is how the statistics are collected.
- Each user gets a private temporary folder for their images. When the PDF is sent (or the user types `/clear`), the folder is deleted.
- When the user types `/pdf`, the bot remembers that it is waiting for a name. The next text message is treated as the PDF name; any other text goes to the admin panel. One function decides this, because Telegram runs only one handler for each message.
- The PDF is built on the disk with a fixed safe name, and the name chosen by the user is used only when sending it. This avoids problems with unusual file names.
- Settings (welcome message, image limit) are stored in the database, so an admin can change them while the bot is running.

## How the statistics are defined

- **New users:** users who used the bot for the first time in that period
- **Active users:** users who sent at least one message or pressed a button in that period
- **Returning users:** joined before this week and used the bot in the last 7 days
- **Regular users:** used the bot on 3 or more different days in the last 30 days
- All times are in UTC

## Run the tests

```bash
python test_db.py
python test_pdf_utils.py
```

The tests check that users are counted once, that new / active / returning / regular users are calculated correctly, that settings and admins work, that the PDF has one page per image (including images with transparency), and that file names are cleaned correctly.

## Privacy and security

- The bot saves each user's Telegram ID, username and first name, only to build the statistics. Images are deleted as soon as the PDF is sent.
- The bot token lives in the `.env` file, which is listed in `.gitignore`, so it is never uploaded to GitHub. The database (`bot.db`) is also excluded.
- Only admins can open the admin panel, and only the owner can add or remove admins. The owner can never be removed.
- If a token was ever shared by mistake, it can be replaced in a few seconds with `/revoke` in @BotFather.

## What I learned

- Building an asynchronous application with an event-driven library, and understanding that only one handler runs for each message
- Designing a small SQLite database and writing SQL queries for the statistics (counting distinct users, grouping by day)
- Keeping secrets out of the code with environment variables and `.gitignore`
- Splitting a project into modules with a single responsibility (Telegram handlers, admin panel, database, PDF logic)
- Handling user input safely, such as cleaning file names and validating numbers
- Writing unit tests, and making the program easy to start for a non-technical user

## Possible improvements

- Let the user reorder or delete a single image before creating the PDF
- Choose the page size (A4 or original image size)
- Add Arabic and English interface languages
- Compress large images to make the PDF smaller
- Run the bot on a hosting service so it works 24 hours a day

## Author

**Osama Mohamed Gamal**
GitHub: [osamamohamedgamal57-star](https://github.com/osamamohamedgamal57-star)
