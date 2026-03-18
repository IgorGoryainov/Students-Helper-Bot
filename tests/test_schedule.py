# -*- coding: utf-8 -*-
"""Tests for bot_logic — schedule lookup and user list I/O."""

import os
import tempfile
from unittest.mock import patch

import pytest

import message_list
from bot_logic import (
    SCHEDULE,
    get_schedule,
    load_user_list,
    save_user_list,
    week_parity,
)


# ---------------------------------------------------------------------------
# week_parity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("iso_week,expected", [
    (2, 1),    # even → 1
    (3, 0),    # odd  → 0
    (10, 1),
    (11, 0),
    (52, 1),   # 52 is even → parity 1
    (1, 0),
])
def test_week_parity(iso_week, expected):
    with patch('bot_logic.datetime') as mock_dt:
        mock_dt.utcnow.return_value.isocalendar.return_value = (2024, iso_week, 1)
        result = week_parity()
    assert result == expected


# ---------------------------------------------------------------------------
# SCHEDULE dict structure
# ---------------------------------------------------------------------------

def test_schedule_has_both_parities():
    assert 0 in SCHEDULE
    assert 1 in SCHEDULE


def test_schedule_covers_all_weekdays():
    for parity in (0, 1):
        for day in range(7):  # 0=Sunday … 6=Saturday
            assert day in SCHEDULE[parity], f"Missing day {day} for parity {parity}"


def test_schedule_weekend_is_holiday():
    assert SCHEDULE[0][0] == 'Выходной'
    assert SCHEDULE[1][0] == 'Выходной'


def test_schedule_weekdays_are_nonempty_strings():
    for parity in (0, 1):
        for day in range(1, 7):
            entry = SCHEDULE[parity][day]
            assert isinstance(entry, str) and len(entry) > 10, \
                f"parity={parity} day={day} looks empty: {entry!r}"


# ---------------------------------------------------------------------------
# get_schedule
# ---------------------------------------------------------------------------

def test_get_schedule_even_monday():
    with patch('bot_logic.week_parity', return_value=1), \
         patch('bot_logic.time') as mock_time:
        mock_time.strftime.return_value = '1'
        mock_time.localtime.return_value = None
        result = get_schedule(0)
    assert result == message_list.msg1_monday


def test_get_schedule_odd_tuesday():
    with patch('bot_logic.week_parity', return_value=0), \
         patch('bot_logic.time') as mock_time:
        mock_time.strftime.return_value = '2'
        mock_time.localtime.return_value = None
        result = get_schedule(0)
    assert result == message_list.msg2_tuesday


def test_get_schedule_tomorrow_saturday_wraps_to_sunday():
    """Saturday (6) + offset 1 → Sunday (0) → 'Выходной'."""
    with patch('bot_logic.week_parity', return_value=1), \
         patch('bot_logic.time') as mock_time:
        mock_time.strftime.return_value = '6'
        mock_time.localtime.return_value = None
        result = get_schedule(1)
    assert result == 'Выходной'


def test_get_schedule_tomorrow_sunday_wraps_to_monday():
    """Sunday (0) + offset 1 → Monday (1)."""
    with patch('bot_logic.week_parity', return_value=1), \
         patch('bot_logic.time') as mock_time:
        mock_time.strftime.return_value = '0'
        mock_time.localtime.return_value = None
        result = get_schedule(1)
    assert result == message_list.msg1_monday


# ---------------------------------------------------------------------------
# load_user_list / save_user_list
# ---------------------------------------------------------------------------

def test_load_empty_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('0\n')
        path = f.name
    try:
        assert load_user_list(path) == []
    finally:
        os.unlink(path)


def test_load_with_users():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('3\n111\n222\n333\n')
        path = f.name
    try:
        assert load_user_list(path) == [111, 222, 333]
    finally:
        os.unlink(path)


def test_load_missing_file_returns_empty():
    result = load_user_list('/tmp/nonexistent_xyz_123.txt')
    assert result == []


def test_save_and_reload_roundtrip():
    users = [100, 200, 300, 400]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        path = f.name
    try:
        save_user_list(path, users)
        assert load_user_list(path) == users
    finally:
        os.unlink(path)


def test_save_and_reload_empty():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        path = f.name
    try:
        save_user_list(path, [])
        assert load_user_list(path) == []
    finally:
        os.unlink(path)


def test_save_preserves_order():
    users = [9, 1, 5, 3, 7]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        path = f.name
    try:
        save_user_list(path, users)
        assert load_user_list(path) == users
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# message_list sanity checks
# ---------------------------------------------------------------------------

def test_material_links_dict_nonempty():
    assert len(message_list.MATERIAL_LINKS) > 0


def test_msg3_contains_all_material_names():
    for name in message_list.MATERIAL_LINKS:
        assert name in message_list.msg3, f"'{name}' not found in msg3"


def test_welcome_message_is_substantial():
    assert len(message_list.msg1) > 50


def test_teacher_contacts_is_substantial():
    assert len(message_list.msg10) > 100


def test_all_schedule_messages_defined():
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    for week in ('msg1', 'msg2'):
        for day in days:
            attr = f'{week}_{day}'
            assert hasattr(message_list, attr), f"message_list.{attr} is missing"
            assert isinstance(getattr(message_list, attr), str)
