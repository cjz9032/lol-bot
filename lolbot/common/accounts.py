"""
Handles multi-platform creating/writing accounts to json file.
"""

import os
import json

from lolbot.common.config import ACCOUNT_PATH


def load_accounts() -> list:
    """Loads all accounts from disk."""
    accounts = []
    if not os.path.exists(ACCOUNT_PATH):
        with open(ACCOUNT_PATH, 'w') as account_file:
            json.dump(accounts, account_file, indent=4)
    try:
        with open(ACCOUNT_PATH, 'r') as account_file:
            accounts = json.load(account_file)
    except json.JSONDecodeError:
        return accounts
    except KeyError:
        return accounts
    if "accounts" in accounts:  # convert old format to new
        accounts = accounts['accounts']
        with open(ACCOUNT_PATH, 'w') as account_file:
            json.dump(accounts, account_file, indent=4)
    return accounts

def save_or_add(account: dict) -> None:
    """If an account with this username already exists, update it. Otherwise, add account."""
    accounts = load_accounts()
    with open(ACCOUNT_PATH, 'w') as account_file:
        exists = False
        for acc in accounts:
            if acc['username'] == account['username']:
                acc.update(account)
            exists = True
        if not exists:
            accounts.append(account)
        json.dump(accounts, account_file, indent=4)


def update(username: str, account: dict) -> None:
    """Updates any field of an account based on the original username."""
    accounts = load_accounts()
    with open(ACCOUNT_PATH, 'w') as account_file:
        for acc in accounts:
            if acc['username'] == username:
                acc.update(account)
        json.dump(accounts, account_file, indent=4)


def delete(username: str) -> None:
    """Removes an account based on the username."""
    accounts = load_accounts()
    with open(ACCOUNT_PATH, 'w') as account_file:
        json.dump([acc for acc in accounts if acc['username'] != username], account_file, indent=4)
