"""Joriy userbot versiyasi"""
__version__ = (2, 0, 0, 7)

import git
import os

try:
    branch = git.Repo(
        path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ).active_branch.name
except Exception:
    branch = "master"
