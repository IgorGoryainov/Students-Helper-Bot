# -*- coding: utf-8 -*-
"""Pure bot logic — no vk_api dependency, fully testable."""

import os
import time
from datetime import datetime

import message_list

SCHEDULE = {
    1: {  # even week (parity=1)
        1: message_list.msg1_monday,
        2: message_list.msg1_tuesday,
        3: message_list.msg1_wednesday,
        4: message_list.msg1_thursday,
        5: message_list.msg1_friday,
        6: message_list.msg1_saturday,
        0: 'Выходной',
    },
    0: {  # odd week (parity=0)
        1: message_list.msg2_monday,
        2: message_list.msg2_tuesday,
        3: message_list.msg2_wednesday,
        4: message_list.msg2_thursday,
        5: message_list.msg2_friday,
        6: message_list.msg2_saturday,
        0: 'Выходной',
    },
}


def week_parity() -> int:
    """Return 1 for even ISO week, 0 for odd."""
    week_number = datetime.utcnow().isocalendar()[1]
    return 1 if week_number % 2 == 0 else 0


def get_schedule(day_offset: int = 0) -> str:
    """Return the schedule string for today (offset=0) or tomorrow (offset=1)."""
    parity = week_parity()
    weekday = (int(time.strftime('%w', time.localtime())) + day_offset) % 7
    return SCHEDULE[parity][weekday]


def load_user_list(path: str) -> list:
    """Load a list of user IDs from a plain-text file (count on first line)."""
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        lines = f.readlines()
    count = int(lines[0])
    return [int(lines[i]) for i in range(1, count + 1)]


def save_user_list(path: str, users: list) -> None:
    """Save a list of user IDs to a plain-text file."""
    with open(path, 'w') as f:
        f.write(str(len(users)) + "\n")
        for uid in users:
            f.write(str(uid) + "\n")
