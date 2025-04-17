"""
Configuration settings for the Snippet Manager Pro application.
"""

import string

# Application info
APP_NAME = "Snippet Manager Pro"
VERSION = "1.0.0"
SAVE_FILE = "snippets.json"

# Category colors for visual distinction
CATEGORY_COLORS = {
    "WordPress Login": "#21759b",     # WordPress blue
    "Instagram Account": "#E1306C",   # Instagram pink
    "Facebook Page": "#4267B2",       # Facebook blue
    "Email Configuration": "#DB4437", # Gmail red
    "Password": "#8A2BE2",            # Purple for passwords
    "default": "#666666"              # Default gray
}

# Theme Colors
LIGHT_THEME = {
    "bg_color": "#f5f5f5",
    "fg_color": "#333333",
    "accent_color": "#2979ff",
    "danger_color": "#f44336",
    "success_color": "#4caf50",
    "secondary_bg": "#ffffff",
    "border_color": "#e0e0e0",
    "selection_color": "#e3f2fd"
}

DARK_THEME = {
    "bg_color": "#333333",
    "fg_color": "#f5f5f5",
    "accent_color": "#2196f3",
    "danger_color": "#e53935",
    "success_color": "#43a047",
    "secondary_bg": "#424242",
    "border_color": "#555555",
    "selection_color": "#455a64"
}

# Password generation options
PASSWORD_CHARS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "special": "!@#$%^&*()-_=+[]{}|;:,.<>?/"
}

# Default settings
DEFAULT_PASSWORD_LENGTH = 16 