import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def secure_password(password):
    """Returns True if password is secure, otherwise returns False"""

    # Minimum length requirement for password
    min_length = 8

    # Ensure password is long enough
    if len(password) < min_length:
        return False

    # Other requirements for password
    # Set minimum number of digits
    min_digits = 1

    # Counter for number of digits, don't change
    digits = 0

    # Set minimum number of uppercase characters
    min_upper = 1

    # Counter for uppercase characters
    upper = 0

    # Set minimum number of special characters
    min_special = 0

    # Counter for special characters
    special = 0

    for c in password:

        if c.isspace():
            return False

        if c.isdigit:
            digits += 1

        if c.isupper:
            upper += 1

        if (33 <= ord(c) <= 47) or (58 <= ord(c) <= 64) or (91 <= ord(c) <= 96) or (123 <= ord(c) <= 126):
            special += 1

    if digits >= min_digits and upper >= min_upper and special >= min_special:
        return True
    else:
        return False