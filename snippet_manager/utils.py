"""
Utility functions for Snippet Manager Pro.
"""

import re
import random
from datetime import datetime
from .config import PASSWORD_CHARS, DEFAULT_PASSWORD_LENGTH

# Add password pattern detection regex - modified to better handle space-separated passwords
PASSWORD_PATTERN = re.compile(r'(?i)(\b(?:password|pass|pwd|secret|token|key|auth|app pass)\s*[:=]\s*)(.+)$', re.MULTILINE)

def adjust_color(color, amount, is_dark_mode=False):
    """Adjust a color by a specified amount."""
    # Convert hex to RGB
    color = color.lstrip('#')
    r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust values
    if is_dark_mode:
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
    else:
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"

def mask_sensitive_data(text):
    """Replace sensitive data like passwords with asterisks."""
    # Find and mask passwords and tokens in the text
    masked_text = PASSWORD_PATTERN.sub(r'\1●●●●●●●●', text)
    return masked_text

def generate_password(length=DEFAULT_PASSWORD_LENGTH, use_uppercase=True, 
                      use_digits=True, use_special=True):
    """Generate a secure random password."""
    # Build character set based on options
    chars = PASSWORD_CHARS["lowercase"]
    if use_uppercase:
        chars += PASSWORD_CHARS["uppercase"]
    if use_digits:
        chars += PASSWORD_CHARS["digits"]
    if use_special:
        chars += PASSWORD_CHARS["special"]
        
    # Generate password
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

def format_current_datetime():
    """Get the current date and time formatted."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S') 