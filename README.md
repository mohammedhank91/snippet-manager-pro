# Snippet Manager Pro

A powerful application for managing text snippets with advanced organization features.

## Features

- Save and organize text snippets with categories
- Markdown rendering support for rich text formatting
- Template system for frequently used snippet formats
- Tag system to organize snippets beyond categories
- Bulk operations for managing multiple snippets
- Dark and light themes
- Password generator with customizable options
- Import and export functionality (TXT, HTML, MD)
- Automatic saving

## New Features

### Markdown Support
- Format your snippets with Markdown syntax
- Live preview of rendered Markdown
- Toggle Markdown mode with a simple checkbox

### Template System
- Save frequently used snippet formats as templates
- Easily create new snippets from templates
- Access all templates from the dedicated Templates tab

### Tag System
- Add multiple tags to any snippet
- Filter snippets by tag
- Manage tags with an intuitive interface

### Bulk Operations
- Select multiple snippets at once
- Perform operations on all selected snippets:
  - Delete
  - Export
  - Change category
  - Add/remove tags
  - Toggle Markdown/Template status

## Screenshots

(Add screenshots of your application here)

## Requirements

- Python 3.9 or higher
- PyQt6
- Markdown library (optional, for Markdown rendering)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application using either:
   ```
   python run_modular.py   # Modular version (recommended)
   ```
   or
   ```
   python run_monolithic.py   # Single-file version
   ```

## Usage

### Managing Snippets
- Add snippets using the "Add Snippet" button
- Edit snippet text and labels directly
- Copy snippet text to clipboard with the "Copy" button
- Delete snippets with the "Delete" button

### Using Templates
1. Create a template by checking the "Template" checkbox
2. Fill in your template content (Markdown is supported)
3. Access all templates from the Templates tab
4. Create new snippets from templates with a single click

### Bulk Operations
1. Enable selection mode using the checkbox
2. Select multiple snippets
3. Click the "Bulk Actions" button to see available operations
4. Choose the operation you want to perform

## User Guide

### Managing Snippets

- **Add Snippet**: Click "Add Snippet" in the toolbar or use Ctrl++
- **Copy Snippet**: Select a snippet and click "Copy" to copy its content
- **Delete Snippet**: Select a snippet and click "Delete" to remove it
- **Copy All**: Click "Copy All" to copy all snippets to clipboard
- **Expand/Collapse**: Click the down/up arrow to resize a snippet
- **Hide Sensitive Data**: Click the eye icon to mask sensitive information

### Managing Categories

1. Navigate to the "Categories" tab
2. Add new categories with custom colors
3. Edit existing categories by selecting them from the list
4. Delete categories you no longer need
5. View snippets associated with each category

### Settings

The Settings tab allows you to:

- Switch between light and dark themes
- Toggle automatic saving
- Enable/disable features

## Project Structure

```
snippet-manager-pro/
├── run_modular.py        # Launcher for modular version
├── run_monolithic.py     # Launcher for monolithic version
├── text_snippet_manager.py # Monolithic implementation
├── requirements.txt      # Dependencies
├── README.md             # This file
└── snippet_manager/      # Modular implementation
    ├── __init__.py       # Package initialization
    ├── main.py           # Application entry point
    ├── config.py         # Configuration settings
    ├── database.py       # Data persistence
    ├── utils.py          # Utility functions
    └── ui/               # User interface components
        ├── __init__.py
        ├── main_window.py  # Main application window
        └── snippet_widget.py # Individual snippet widget
```

## Troubleshooting

- **PyQt6 Import Errors**: Make sure you've installed PyQt6 correctly: `pip install PyQt6==6.5.0`
- **No module named 'snippet_manager'**: Make sure you're running from the root directory of the project
- **UI Layout Issues**: If the UI looks wrong, check for Qt version compatibility

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
