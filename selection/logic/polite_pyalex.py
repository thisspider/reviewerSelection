"""Wrapper for pyalex to use the polite pool by authenticating.

The polite pool has much faster and more consistent response times.
To get into the polite pool, you set your email.
"""

import subprocess

import pyalex


def get_git_user():
    res = subprocess.run(["git", "config", "user.email"], stdout=subprocess.PIPE)
    return res.stdout.strip().decode()


pyalex.config.email = get_git_user()
