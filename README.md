# Images to PDF - Telegram Bot

A Telegram bot that turns your photos into a single PDF file, with the name you choose. Send it your images, type `/pdf`, tell it what to call the file, and the PDF comes back in a few seconds. The bot also keeps simple usage statistics and has an admin panel inside Telegram, so it can be managed without touching the code.

I wrote the whole project in Python. It runs on my own computer (no paid hosting): I start it by double-clicking one file, `run_bot.bat`.

## Quick facts

| | |
|---|---|
| **What it does** | Converts images to one PDF, with a custom file name |
| **Where to use it** | Telegram: [@YOUR_BOT_USERNAME](https://t.me/YOUR_BOT_USERNAME) |
| **Language** | Python 3 |
| **Main libraries** | python-telegram-bot, Pillow, python-dotenv |
| **Database** | SQLite (`bot.db`, created automatically) |
| **Runs on** | My own Windows computer, started with `run_bot.bat` |
| **Tests** | 14 automated unit tests |
| **Author** | Osama Mohamed Gamal |

## How to try the bot (for reviewers)

You do not need to install anything. You only need Telegram.

1. Open Telegram and search for **@YOUR_BOT_USERNAME**, or open this link: https://t.me/YOUR_BOT_USERNAME
2. Press **Start** (or type `/start`). The bot replies with a short welcome message that explains the steps.
3. Send it **2 or 3 photos**. You can send them one by one, as an album, or as files. After each image the bot answers `Image 1 saved`, `Image 2 saved`, and so on.
4. Type `/pdf`. The bot asks: **"What should the PDF be called?"**
5. Type any name, for example `My test file`. (You do not need to type `.pdf`. Type `/skip` if you want the default name `images.pdf`.)
6. The bot sends you `My test file.pdf`, with one page for every photo, in the same order you sent them.

Example conversation:

```
You:  /start
Bot:  Hi! I turn your images into one PDF. ...
You:  [photo 1]
Bot:  Image 1 saved. Send more, or type /pdf.
You:  [photo 2]
Bot:  Image 2 saved. Send more, or type /pdf.
You:  /pdf
Bot:  What should the PDF be called?
      Send me the name now (no need to type .pdf). ...
You:  My test file
Bot:  Creating My test file.pdf ...
Bot:  [My test file.pdf]
```

Other things you can try:

- `/clear` deletes the images you sent so you can start again.
- `/cancel` cancels the question about the name. Your images stay saved.
- Type `/admin`. Because you are not an admin, the bot answers `Sorry, this command is for admins only.` This shows that the admin panel is protected.

**Important:** the bot runs on my personal computer, so it answers only while my computer is turned on and connected to the internet. If the bot does not reply, it simply means my computer is off at that moment. Please try again later, or contact me through my GitHub profile and I will start it.

<!-- To add screenshots: create a folder named screenshots in this repo, upload your images there, then replace this line with:
![Creating a PDF](screenshots/create-pdf.png)
![Admin panel](screenshots/admin-panel.png)
![Statistics](screenshots/statistics.png) -->

## Why I built it

I wanted a project that goes beyond a web page: a real application that other people can use from their phones, with a database, an admin side and proper error handling. A bot that converts photos to PDF solves a problem I actually have (sending several photos as one document), and it let me practise the skills of a complete back-end project: handling asynchronous events, storing data in a database, separating the code into modules, keeping secrets out of the code, and writing automated tests.

## Features

**For users**
- Accepts normal photos and images sent as files (one by one or as an album)
- **Custom file name:** after `/pdf`, the bot asks what the file should be called (or type `/skip` for the default name)
- One PDF page per image, in the same order the images were sent
- Photos taken sideways are rotated correctly (EXIF orientation)
- Images with transparency (like PNG) are converted safely
- Arabic and other languages work in file names
- The user's images are deleted right after the PDF is sent

**For admins** (type `/admin` in Telegram)
- **Statistics:** total users, new users (today / 7 days / 30 days), active users (today / 7 days / 30 days), returning users, regular users, and the number of PDFs created
- **Edit the welcome message** from Telegram, without changing the code
- **Change the maximum number of images** per PDF (from 1 to 100)
- **Manage admins:** the owner can add and remove other admins

**Reliability and safety**
- The name typed by the user is cleaned first: characters that are not allowed in file names (`\ / : * ? " < > |`) are removed, the length is limited to 100 characters, and `.pdf` is never doubled
- If a file is not a valid image, the bot answers with a clear message instead of crashing
- A limit on the number of images per PDF protects the computer from huge uploads
- Each user works in a private temporary folder, so users never see each other's files

## Commands

| Command | Who | What it does |
|---|---|---|
| `/start` | everyone | Shows the welcome message |
| `/pdf` | everyone | Asks for the PDF name, then creates and sends the file |
| `/skip` | everyone | Uses the default name (`images.pdf`) when the bot asks for a name |
| `/clear` | everyone | Deletes your images and starts over |
| `/cancel` | everyone | Cancels the question about the name (images stay saved), or cancels an admin edit |
| `/admin` | admins | Opens the admin panel |
| `/addadmin ID` | owner | Adds a new admin (by Telegram ID) |
| `/removeadmin ID` | owner | Removes an admin. The owner can never be removed |

## The admin panel

The admin panel is a message with buttons. Only admins can open it.

| Button | What it does |
|---|---|
| 📊 **Statistics** | Shows how many people use the bot and how many PDFs were created |
| ✏️ **Edit welcome message** | Shows the current message; the next message the admin sends becomes the new welcome message |
| 🔢 **Change max images** | The admin sends a number from 1 to 100; this is the new limit per PDF |
| 👥 **Admins** | Lists the admin IDs and explains how the owner adds or removes admins |
| ⬅️ **Back** | Returns to the main panel |

## Built with

- **Python 3** for all the code
- **python-telegram-bot** (async version) to talk to Telegram
- **SQLite** (built into Python) to store users, activity, PDFs, settings and admins
- **Pillow** to open the images and build the PDF
- **python-dotenv** to keep the bot token outside the code
- **unittest** for the automated tests

## Project structure

This is the same list of files that you see on the GitHub page of this project:

```
images-to-pdf/
├── .env.example      # Template that shows how the private settings file looks
├── .gitignore        # List of files that Git should ignore
├── README.md         # This file: the project description
├── admin.py          # Admin panel: buttons, settings, admin management
├── bot.py            # Main program: starts the bot and handles the messages
├── db.py             # Database code: users, activity, PDFs, settings, admins
├── pdf_utils.py      # Builds the PDF and cleans the file name
├── requirements.txt  # Python libraries the project needs
├── run_bot.bat       # Double-click launcher for Windows
├── test_db.py        # Unit tests for the database and the statistics
└── test_pdf_utils.py # Unit tests for the PDF creation and the name cleaning
```

### What each file does

| File | Purpose |
|---|---|
| `bot.py` | The entry point. It reads the settings, prepares the database, connects to Telegram and registers every command. It also receives the images, asks for the PDF name and sends the finished file. |
| `admin.py` | Everything about the admin side: the panel buttons, the statistics message, editing the settings, and adding or removing admins. |
| `db.py` | The only file that talks to the database. It saves users and their daily activity, counts the PDFs, calculates the statistics, and stores the settings and the admin list. |
| `pdf_utils.py` | `images_to_pdf()` builds the PDF from a list of image files. `clean_pdf_name()` turns the text typed by the user into a safe file name. |
| `run_bot.bat` | Starts the bot on Windows with a double-click (see below). |
| `requirements.txt` | The libraries to install: `python-telegram-bot`, `Pillow` and `python-dotenv`. |
| `.env.example` | An example of the private settings file, with fake values. The real `.env` file (with the bot token and the owner's Telegram ID) exists only on my computer and is not uploaded to GitHub. |
| `.gitignore` | Tells Git to ignore the private `.env` file, the database `bot.db` and Python's cache files. |
| `test_db.py`, `test_pdf_utils.py` | The automated tests. |

On my computer there are also two files that are not uploaded to GitHub: the private `.env` file (the bot token and my Telegram ID) and the database `bot.db`, which the bot creates by itself the first time it starts.

## How it works

**The big picture**

```
 User in Telegram
        │  sends photos, /pdf, a name
        ▼
 Telegram servers  ◄───────────────  bot.py asks "any new messages?" (polling)
        │
        ▼
 bot.py ── saves the user ──► db.py ──► bot.db
   │
   ├── saves each photo in the user's private temporary folder
   ├── asks for the PDF name
   ├── pdf_utils.py builds the PDF
   ├── sends the PDF back to the user
   └── deletes the temporary folder
```

**Step by step**

1. **Polling.** The bot asks Telegram all the time: "is there a new message for me?". Because the bot starts the conversation with Telegram (and not the other way around), it needs no public web address, so it can run from a normal home computer.
2. **Counting users.** Every message first passes through a small handler that saves the user and marks them as active today. This is how the statistics are collected.
3. **Receiving images.** Each photo is downloaded into a private temporary folder that belongs to that user. For normal photos, the bot downloads the biggest size that Telegram offers.
4. **Asking for the name.** When the user types `/pdf`, the bot does not create the file immediately. It remembers that it is waiting for a name. The next text message is used as the name of the PDF.
5. **One function decides who gets a text message.** Telegram runs only one handler for each message. The same plain text can be a PDF name or an admin edit (for example a new welcome message), so a single function `text_router` checks the situation and sends the text to the right place.
6. **Creating the PDF.** `images_to_pdf()` opens every image, fixes its rotation, converts it to RGB (a PDF page cannot be transparent) and saves all of them as pages of one PDF.
7. **Safe file name.** The PDF is built on the disk with a fixed safe name (`output.pdf`). The name chosen by the user is used only when the file is sent to Telegram. This avoids problems with strange characters.
8. **Cleaning up.** After the PDF is sent (or if something fails, or if the user types `/clear`), the temporary folder is deleted.
9. **Settings in the database.** The welcome message and the image limit are stored in the database, so an admin can change them while the bot is running.

## The database

The database has five small tables:

| Table | What it stores |
|---|---|
| `users` | Telegram ID, username, first name, first time seen, last time seen |
| `activity` | One row for every user and every day the user used the bot (used for the active / returning / regular statistics) |
| `pdfs` | One row for every PDF created: who, when, and how many pages |
| `settings` | The welcome message and the maximum number of images |
| `admins` | The Telegram IDs of the admins |

All times are saved in UTC.

## How the statistics are defined

- **New users:** users who used the bot for the first time in that period
- **Active users:** users who sent at least one message or pressed a button in that period
- **Returning users:** users who joined before this week and used the bot again in the last 7 days
- **Regular users:** users who used the bot on 3 or more different days in the last 30 days
- **PDFs created:** the total number, and the number created today
- All times are in UTC

## How I start the bot

I double-click `run_bot.bat`. This small script:

1. Moves to the folder of the project, so it works from anywhere.
2. Checks that Python is installed.
3. Creates the `.env` file from `.env.example` if it does not exist yet.
4. Installs the libraries from `requirements.txt` if one of them is missing.
5. Starts `bot.py`.

The bot works as long as the black window stays open. Closing the window (or pressing `Ctrl+C`) stops the bot.

## Run the tests

The tests do not need a Telegram token or an internet connection. With Python and the libraries from `requirements.txt` installed, run:

```bash
python test_db.py
python test_pdf_utils.py
```

The tests check that:

- the same user is counted only once
- new, active, returning and regular users are calculated correctly
- inactive users are not counted as active
- PDFs are counted correctly (total and today)
- settings and admins can be saved, changed and removed
- the PDF has one page for every image, including images with transparency
- an empty list of images gives a clear error
- file names are cleaned correctly (extra `.pdf`, forbidden characters, empty names, Arabic names, very long names)

## Privacy and security

- **What the bot stores:** the Telegram ID, username and first name of each user, only to build the statistics. It also stores the date and the number of pages of each PDF.
- **Images are never kept.** They are saved in a temporary folder only until the PDF is sent, then deleted.
- **The token is not written inside the code.** The code reads it from a private `.env` file that stays on my computer. It is not uploaded to GitHub, and `.gitignore` is set to keep it (and the database `bot.db`) out of Git.
- **Admin protection:** only admins can open the admin panel, and only the owner can add or remove admins. The owner can never be removed.
- **Safe input:** file names typed by users are cleaned, and the image limit is checked before every download.

## What I learned

- Building an asynchronous application with an event-driven library, and understanding that only one handler runs for each message
- Designing a small SQLite database and writing SQL queries for the statistics (counting distinct users, grouping by day)
- Keeping secrets out of the code with environment variables
- Splitting a project into modules where each file has one job (Telegram handlers, admin panel, database, PDF logic)
- Handling user input safely, such as cleaning file names and validating numbers
- Writing unit tests, and making the program easy to start for someone who is not technical

## Possible improvements

- Let the user reorder or delete a single image before creating the PDF
- Choose the page size (A4 or the original image size)
- Add Arabic and English interface languages
- Compress large images to make the PDF smaller
- Run the bot on a hosting service so it works 24 hours a day

## Author

**Osama Mohamed Gamal**
GitHub: [osamamohamedgamal57-star](https://github.com/osamamohamedgamal57-star)
