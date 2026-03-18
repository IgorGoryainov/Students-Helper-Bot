# iu1-schedule-bot

VK bot for the IU1-21 student group at BMSTU. Sends class schedules, study materials, and teacher contacts on demand. The group elder can broadcast messages to all registered students.

## What it does

- Returns today's or tomorrow's schedule (handles even/odd academic weeks automatically)
- Sends links to study materials (homework, lab guides, exam prep)
- Lists teacher contact info
- Lets the group elder broadcast announcements to all registered users

## Stack

- Python 3.8+
- [vk_api](https://github.com/python273/vk_api) — VK Bot Long Poll API

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Configure the VK token**

Copy `.env.example` to `.env` and fill in your VK API token:

```bash
cp .env.example .env
# edit .env and set VK_TOKEN=your_token
```

Or export it directly:

```bash
export VK_TOKEN=your_vk_api_token
```

**3. Initialize state files**

On first run, the bot needs empty state files:

```bash
cp id_list.txt.example id_list.txt
cp id_board.txt.example id_board.txt
```

**4. Run**

```bash
python main.py
```

## Notes

- `id_list.txt` — tracks registered users (created/updated at runtime, not versioned)
- `id_board.txt` — tracks mailing list subscribers (same)
- The elder's VK user ID is hardcoded in `main.py` (`elder_id`)
- Schedules are defined in `message_list.py` — update them each semester
