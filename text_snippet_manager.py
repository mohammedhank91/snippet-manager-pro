import sys
import os
import json
import platform
import random
import string
import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QFrame, 
    QMenu, QMenuBar, QStatusBar, QFileDialog, QDialog, 
    QTabWidget, QSplitter, QTextEdit, QComboBox, QCheckBox,
    QListWidget, QListWidgetItem, QGridLayout, QToolBar, QToolButton,
    QMessageBox, QSpacerItem, QSizePolicy, QColorDialog, QInputDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer, QUrl, pyqtSignal, QEvent
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QKeySequence, QTextCursor

# Configuration
APP_NAME = "Snippet Manager Pro"
VERSION = "1.0.0"
SAVE_FILE = "snippets.json"

# Category colors for visual distinction
CATEGORY_COLORS = {
    "WordPress Login": "#21759b",     # WordPress blue
    "Instagram Account": "#E1306C",   # Instagram pink
    "Facebook Page": "#4267B2",       # Facebook blue
    "Email Configuration": "#DB4437", # Gmail red
    "Password": "#FF5733",            # Password orange
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

# Add password pattern detection regex
PASSWORD_PATTERN = re.compile(r'(?i)(\b(?:password|pass|pwd|secret|token|key|auth)\s*[:=]\s*)([^\s]+)')

class TextSnippetManager(QMainWindow):
    """Main application window for Text Snippet Manager Pro with PyQt6."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(APP_NAME)
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # Application state
        self.is_dark_mode = False
        self.snippets = []
        self.current_theme = LIGHT_THEME.copy()
        
        # Set up the UI
        self.setup_ui()
        
        # Load saved snippets
        self.load_snippets()
        
        # Center window on screen
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen."""
        screen_geometry = QApplication.primaryScreen().geometry()
        window_geometry = self.geometry()
        
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        
        self.move(x, y)

    def setup_ui(self):
        """Set up the user interface."""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create tabs
        self.create_tabs()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.show_status("Ready")
        
        # Apply theme
        self.apply_theme()
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.clear_all_snippets)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.import_snippets)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_snippets)
        file_menu.addAction(save_action)
        
        export_menu = QMenu("&Export", self)
        file_menu.addMenu(export_menu)
        
        export_txt_action = QAction("Export as &Text", self)
        export_txt_action.triggered.connect(lambda: self.export_snippets("txt"))
        export_menu.addAction(export_txt_action)
        
        export_html_action = QAction("Export as &HTML", self)
        export_html_action.triggered.connect(lambda: self.export_snippets("html"))
        export_menu.addAction(export_html_action)
        
        export_md_action = QAction("Export as &Markdown", self)
        export_md_action.triggered.connect(lambda: self.export_snippets("md"))
        export_menu.addAction(export_md_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = QMenu("&Edit", self)
        self.menu_bar.addMenu(edit_menu)
        
        add_action = QAction("&Add Snippet", self)
        add_action.setShortcut(QKeySequence("Ctrl++"))
        add_action.triggered.connect(self.add_snippet)
        edit_menu.addAction(add_action)
        
        copy_all_action = QAction("&Copy All", self)
        copy_all_action.setShortcut(QKeySequence("Ctrl+A"))
        copy_all_action.triggered.connect(self.copy_all_snippets)
        edit_menu.addAction(copy_all_action)
        
        clear_all_action = QAction("Clear &All", self)
        clear_all_action.setShortcut(QKeySequence("Ctrl+D"))
        clear_all_action.triggered.connect(self.clear_all_snippets)
        edit_menu.addAction(clear_all_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        self.menu_bar.addMenu(view_menu)
        
        toggle_theme_action = QAction("&Toggle Theme", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        self.menu_bar.addMenu(help_menu)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)
        
    def create_toolbar(self):
        """Create the application toolbar."""
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.toolbar)
        
        add_btn = QToolButton()
        add_btn.setText("Add Snippet")
        add_btn.setToolTip("Add a new snippet")
        add_btn.clicked.connect(self.add_snippet)
        self.toolbar.addWidget(add_btn)
        
        copy_all_btn = QToolButton()
        copy_all_btn.setText("Copy All")
        copy_all_btn.setToolTip("Copy all snippets to clipboard")
        copy_all_btn.clicked.connect(self.copy_all_snippets)
        self.toolbar.addWidget(copy_all_btn)
        
        clear_all_btn = QToolButton()
        clear_all_btn.setText("Clear All")
        clear_all_btn.setToolTip("Clear all snippets")
        clear_all_btn.clicked.connect(self.clear_all_snippets)
        self.toolbar.addWidget(clear_all_btn)
        
        self.toolbar.addSeparator()
        
        import_btn = QToolButton()
        import_btn.setText("Import")
        import_btn.setToolTip("Import snippets from file")
        import_btn.clicked.connect(self.import_snippets)
        self.toolbar.addWidget(import_btn)
        
        export_btn = QToolButton()
        export_btn.setText("Export")
        export_btn.setToolTip("Export snippets to file")
        export_btn.clicked.connect(lambda: self.export_snippets("txt"))
        self.toolbar.addWidget(export_btn)
        
        # Add password generator button
        password_gen_btn = QToolButton()
        password_gen_btn.setText("Generate Password")
        password_gen_btn.setToolTip("Generate a secure random password")
        password_gen_btn.clicked.connect(self.generate_password)
        self.toolbar.addWidget(password_gen_btn)
        
        self.toolbar.addSeparator()
        
        # Right-aligned items
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)
        
        theme_btn = QToolButton()
        theme_btn.setText("Toggle Theme")
        theme_btn.setToolTip("Switch between light and dark theme")
        theme_btn.clicked.connect(self.toggle_theme)
        self.toolbar.addWidget(theme_btn)
        
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.is_dark_mode = not self.is_dark_mode
        self.current_theme = DARK_THEME.copy() if self.is_dark_mode else LIGHT_THEME.copy()
        self.apply_theme()
        
        theme_name = "Dark" if self.is_dark_mode else "Light"
        self.show_status(f"Switched to {theme_name} Theme")
        
    def apply_theme(self):
        """Apply the current theme to all UI elements."""
        # Get current theme colors
        bg_color = self.current_theme["bg_color"]
        fg_color = self.current_theme["fg_color"]
        accent_color = self.current_theme["accent_color"]
        secondary_bg = self.current_theme["secondary_bg"]
        border_color = self.current_theme["border_color"]
        
        # Define stylesheet
        qss = f"""
            QMainWindow, QWidget {{
                background-color: {bg_color};
                color: {fg_color};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {border_color};
                background-color: {secondary_bg};
            }}
            
            QTabBar::tab {{
                background-color: {bg_color};
                color: {fg_color};
                padding: 8px 12px;
                border: 1px solid {border_color};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {secondary_bg};
                border-bottom: 2px solid {accent_color};
            }}
            
            QPushButton, QToolButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
            }}
            
            QPushButton:hover, QToolButton:hover {{
                background-color: {self.adjust_color(accent_color, 20)};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {secondary_bg};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QComboBox {{
                background-color: {secondary_bg};
                color: {fg_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {border_color};
            }}
            
            QTextEdit {{
                font-size: 11px;
            }}
            
            QScrollArea {{
                border: 1px solid {border_color};
                border-radius: 4px;
            }}
            
            QStatusBar {{
                border-top: 1px solid {border_color};
                background-color: {bg_color};
            }}
            
            QToolBar {{
                border: none;
                background-color: {bg_color};
                spacing: 5px;
            }}
            
            QMenuBar {{
                background-color: {bg_color};
                color: {fg_color};
            }}
            
            QMenuBar::item:selected {{
                background-color: {self.adjust_color(bg_color, 20)};
            }}
            
            QMenu {{
                background-color: {secondary_bg};
                color: {fg_color};
                border: 1px solid {border_color};
            }}
            
            QMenu::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
        """
        
        # Apply stylesheet
        self.setStyleSheet(qss)
        
        # Update frames based on category colors
        for snippet in self.snippets:
            category = snippet["label_edit"].text()
            category_color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["default"])
            snippet["frame"].setStyleSheet(f"""
                QFrame {{
                    border-left: 5px solid {category_color};
                    background-color: {secondary_bg};
                    border-radius: 4px;
                    margin-bottom: 5px;
                }}
            """)
            
            # Update label colors
            snippet["label_edit"].setStyleSheet(f"""
                QLineEdit {{
                    font-weight: bold;
                    font-size: 13px;
                    color: {category_color};
                    border: none;
                    background-color: transparent;
                }}
            """)
    
    def adjust_color(self, color, amount):
        """Adjust a color by a specified amount."""
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Adjust values
        if self.is_dark_mode:
            r = min(255, r + amount)
            g = min(255, g + amount)
            b = min(255, b + amount)
        else:
            r = max(0, r - amount)
            g = max(0, g - amount)
            b = max(0, b - amount)
            
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def show_status(self, message, timeout=3000):
        """Display a message in the status bar."""
        self.status_bar.showMessage(message, timeout)

    def create_tabs(self):
        """Create the tab widget with different views."""
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create snippets tab
        self.snippets_tab = QWidget()
        self.tabs.addTab(self.snippets_tab, "Snippets")
        
        # Create categories tab (for future organization)
        self.categories_tab = QWidget()
        self.tabs.addTab(self.categories_tab, "Categories")
        
        # Create settings tab
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Set up snippets tab
        self.setup_snippets_tab()
        self.setup_categories_tab()
        self.setup_settings_tab()
        
    def setup_snippets_tab(self):
        """Set up the snippets tab with scrollable area."""
        snippets_layout = QVBoxLayout(self.snippets_tab)
        
        # Add category filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by category:")
        filter_layout.addWidget(filter_label)
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentIndexChanged.connect(self.apply_category_filter)
        filter_layout.addWidget(self.category_filter)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search snippets...")
        self.search_box.textChanged.connect(self.search_snippets)
        search_layout.addWidget(self.search_box)
        
        # Add filter and search to top of layout
        filter_search_layout = QHBoxLayout()
        filter_search_layout.addLayout(filter_layout)
        filter_search_layout.addLayout(search_layout)
        snippets_layout.addLayout(filter_search_layout)
        
        # Create scroll area for snippets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        snippets_layout.addWidget(scroll_area)
        
        # Create container widget for scroll area
        self.scroll_content = QWidget()
        scroll_area.setWidget(self.scroll_content)
        
        # Create layout for snippets
        self.snippets_layout = QVBoxLayout(self.scroll_content)
        self.snippets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.snippets_layout.setContentsMargins(0, 0, 0, 0)
        self.snippets_layout.setSpacing(10)
    
    def setup_categories_tab(self):
        """Set up the categories tab for organizing snippets (future feature)."""
        categories_layout = QVBoxLayout(self.categories_tab)
        
        # Information label
        info_label = QLabel("Categories will allow you to organize your snippets by topic.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        categories_layout.addWidget(info_label)
        
        # Categories will be implemented in a future update
        coming_soon = QLabel("Coming Soon!")
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet("font-size: 18pt; font-weight: bold;")
        categories_layout.addWidget(coming_soon)
    
    def setup_settings_tab(self):
        """Set up the settings tab with application configuration options."""
        settings_layout = QVBoxLayout(self.settings_tab)
        
        # Theme settings
        theme_group = QFrame()
        theme_group.setFrameShape(QFrame.Shape.StyledPanel)
        theme_layout = QVBoxLayout(theme_group)
        
        theme_label = QLabel("Theme Settings")
        theme_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        theme_layout.addWidget(theme_label)
        
        # Theme selector
        theme_selector_layout = QHBoxLayout()
        theme_selector_label = QLabel("Theme:")
        theme_selector_layout.addWidget(theme_selector_label)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.setCurrentIndex(1 if self.is_dark_mode else 0)
        self.theme_selector.currentIndexChanged.connect(self.on_theme_selected)
        theme_selector_layout.addWidget(self.theme_selector)
        
        theme_layout.addLayout(theme_selector_layout)
        settings_layout.addWidget(theme_group)
        
        # Snippet settings
        snippet_group = QFrame()
        snippet_group.setFrameShape(QFrame.Shape.StyledPanel)
        snippet_layout = QVBoxLayout(snippet_group)
        
        snippet_label = QLabel("Snippet Settings")
        snippet_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        snippet_layout.addWidget(snippet_label)
        
        # Auto-save option
        auto_save_layout = QHBoxLayout()
        self.auto_save_checkbox = QCheckBox("Automatically save snippets when modified")
        self.auto_save_checkbox.setChecked(True)
        auto_save_layout.addWidget(self.auto_save_checkbox)
        snippet_layout.addLayout(auto_save_layout)
        
        # Rich text editing option
        rich_text_layout = QHBoxLayout()
        self.rich_text_checkbox = QCheckBox("Enable rich text editing (formatting)")
        self.rich_text_checkbox.setChecked(False)
        rich_text_layout.addWidget(self.rich_text_checkbox)
        snippet_layout.addLayout(rich_text_layout)
        
        settings_layout.addWidget(snippet_group)
        
        # About group
        about_group = QFrame()
        about_group.setFrameShape(QFrame.Shape.StyledPanel)
        about_layout = QVBoxLayout(about_group)
        
        about_label = QLabel("About")
        about_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        about_layout.addWidget(about_label)
        
        about_app_label = QLabel(f"{APP_NAME} - Version {VERSION}")
        about_layout.addWidget(about_app_label)
        
        settings_layout.addWidget(about_group)
        
        # Add spacer to push everything to the top
        settings_layout.addStretch()
    
    def on_theme_selected(self, index):
        """Handle theme selection from the dropdown."""
        self.is_dark_mode = (index == 1)
        self.toggle_theme()
    
    def add_snippet(self, text="", label=""):
        """Add a new snippet to the collection."""
        # Create a frame for this snippet
        snippet_frame = QFrame()
        snippet_frame.setFrameShape(QFrame.Shape.StyledPanel)
        snippet_frame.setLineWidth(1)
        
        # Check if this is a password-related snippet
        is_password = any(term in label.lower() for term in ['password', 'pass', 'pwd', 'secret']) or text.lower().startswith("password:")
        
        # Set category color if it matches one of our predefined categories or is password-related
        if is_password:
            category_color = CATEGORY_COLORS["Password"]
        else:
            category_color = CATEGORY_COLORS.get(label, CATEGORY_COLORS["default"])
            
        snippet_frame.setStyleSheet(f"""
            QFrame {{
                border-left: 5px solid {category_color};
                background-color: {self.current_theme['secondary_bg']};
                border-radius: 4px;
                margin-bottom: 5px;
            }}
        """)
        
        snippet_layout = QGridLayout(snippet_frame)
        snippet_layout.setContentsMargins(10, 10, 10, 10)
        snippet_layout.setVerticalSpacing(0)  # Remove spacing between rows
        
        # Add row number
        row_num = len(self.snippets) + 1
        row_label = QLabel(f"{row_num}.")
        snippet_layout.addWidget(row_label, 0, 0)
        
        # Add label/description field with better styling
        label_edit = QLineEdit(label)
        label_edit.setPlaceholderText("Snippet Description")
        label_edit.setStyleSheet(f"""
            QLineEdit {{
                font-weight: bold;
                font-size: 13px;
                color: {category_color};
                border: none;
                background-color: transparent;
            }}
        """)
        snippet_layout.addWidget(label_edit, 0, 1)
        
        # Add text edit field (can be expanded to rich text later)
        text_content = str(text) if text else ""  # Ensure text is a string
        text_edit = QTextEdit()
        text_edit.setText(text_content)
        text_edit.setAcceptRichText(False)
        text_edit.setPlaceholderText("Enter your snippet text here...")
        
        # Make the text edit expandable instead of fixed height
        text_edit.setMinimumHeight(70)  # Minimum height
        text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Add a resize grip indicator in the style
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                font-size: 11px;
                background-color: {self.current_theme['secondary_bg']};
                color: {self.current_theme['fg_color']};
                border: 1px solid {self.current_theme['border_color']};
                border-radius: 4px;
                padding: 5px;
            }}
        """)
        
        snippet_layout.addWidget(text_edit, 1, 0, 1, 3)
        
        # Add button row
        button_layout = QHBoxLayout()
        
        # Add expand/collapse button
        expand_btn = QPushButton("⬍")  # Down arrow Unicode character
        expand_btn.setToolTip("Expand/Collapse")
        expand_btn.setFixedWidth(30)
        expand_btn.setStyleSheet(f"background-color: {category_color};")
        expand_btn.clicked.connect(lambda: self.toggle_snippet_expansion(text_edit))
        
        # Add hide/show sensitive data button
        mask_btn = QPushButton("👁️")  # Eye Unicode character
        mask_btn.setToolTip("Hide/Show Sensitive Data")
        mask_btn.setFixedWidth(30)
        mask_btn.setStyleSheet(f"background-color: {category_color};")
        mask_btn.clicked.connect(lambda: self.toggle_sensitive_data(text_edit))
        
        button_layout.addWidget(expand_btn)
        button_layout.addWidget(mask_btn)
        button_layout.addStretch()
        
        snippet_layout.addLayout(button_layout, 0, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        
        # Add snippet actions
        actions_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(lambda: self.copy_snippet(text_edit))
        actions_layout.addWidget(copy_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet(f"background-color: {self.current_theme['danger_color']};")
        delete_btn.clicked.connect(lambda: self.delete_snippet(snippet_frame))
        actions_layout.addWidget(delete_btn)
        
        # Add spacer before actions
        actions_layout.addStretch()
        
        snippet_layout.addLayout(actions_layout, 2, 0, 1, 3)
        
        # Add the snippet to the UI
        self.snippets_layout.addWidget(snippet_frame)
        
        # Store snippet information
        snippet_data = {
            "frame": snippet_frame,
            "label_edit": label_edit,
            "text_edit": text_edit,
            "row_num": row_num,
            "row_label": row_label,
            "expand_btn": expand_btn,
            "mask_btn": mask_btn,
            "is_expanded": False,
            "is_masked": False,
            "original_text": text_content
        }
        self.snippets.append(snippet_data)
        
        # Connect editing signals for auto-save
        label_edit.textChanged.connect(self.on_snippet_changed)
        text_edit.textChanged.connect(self.on_snippet_changed)
        text_edit.textChanged.connect(lambda: self.update_original_text(text_edit))
        
        # Focus the text field
        text_edit.setFocus()
        
        # Update row numbers
        self.update_row_numbers()
        
        # Add category to filter if it's not already there
        if label and self.category_filter.findText(label) == -1:
            self.category_filter.addItem(label)
        
        self.show_status(f"Added new snippet #{row_num}")
        return snippet_data
    
    def update_row_numbers(self):
        """Update the row numbers after deletion or addition."""
        for i, snippet in enumerate(self.snippets, 1):
            snippet["row_num"] = i
            snippet["row_label"].setText(f"{i}.")
    
    def delete_snippet(self, snippet_frame):
        """Delete a snippet from the collection."""
        # Find the snippet in our collection
        for snippet in self.snippets:
            if snippet["frame"] == snippet_frame:
                row_num = snippet["row_num"]
                # Remove from UI
                snippet_frame.deleteLater()
                # Remove from collection
                self.snippets.remove(snippet)
                # Update row numbers
                self.update_row_numbers()
                # Save changes
                self.save_snippets()
                
                self.show_status(f"Deleted snippet #{row_num}")
                break
    
    def copy_snippet(self, text_edit):
        """Copy the text from a snippet to the clipboard."""
        text = text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.show_status(f"Copied: {text[:30]}{'...' if len(text) > 30 else ''}")
        else:
            self.show_status("Nothing to copy - snippet is empty!")
    
    def copy_all_snippets(self):
        """Copy all snippet texts concatenated to the clipboard."""
        all_texts = "\n".join(snippet["text_edit"].toPlainText() 
                             for snippet in self.snippets 
                             if snippet["text_edit"].toPlainText().strip())
        
        if all_texts:
            QApplication.clipboard().setText(all_texts)
            count = sum(1 for snippet in self.snippets 
                      if snippet["text_edit"].toPlainText().strip())
            self.show_status(f"Copied all {count} snippets to clipboard")
        else:
            self.show_status("Nothing to copy - all snippets are empty!")
    
    def clear_all_snippets(self):
        """Clear all snippets and add one empty snippet."""
        if self.snippets:
            for snippet in self.snippets:
                snippet["frame"].deleteLater()
            
            count = len(self.snippets)
            self.snippets.clear()
            self.add_snippet()
            self.save_snippets()
            
            self.show_status(f"Cleared all {count} snippets")
        else:
            self.show_status("No snippets to clear")
    
    def on_snippet_changed(self):
        """Handle snippet content changes."""
        if self.auto_save_checkbox.isChecked():
            # Use a timer to debounce the save operation
            QTimer.singleShot(1000, self.save_snippets)
    
    def save_snippets(self):
        """Save all snippets to the JSON file."""
        snippets_data = []
        
        for snippet in self.snippets:
            text = snippet["text_edit"].toPlainText()
            label = snippet["label_edit"].text()
            snippets_data.append({
                "text": text,
                "label": label
            })
        
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(snippets_data, f)
            self.show_status(f"Saved {len(snippets_data)} snippets")
            return True
        except Exception as e:
            self.show_status(f"Error saving: {str(e)}")
            return False
    
    def load_snippets(self):
        """Load snippets from the JSON file."""
        # Add default credentials snippets if file doesn't exist
        if not os.path.exists(SAVE_FILE):
            # WordPress site credentials
            wp_creds = """Site name: Picayune Fire
            URL: https://picayunefire.s1-tastewp.com
            Username: admin
            Password: sFmKkoOPW_g
            app pass: GAX3 2Bwj iEE3 Hau5 EA7Y kuo3"""
            
            # Create organized snippets with appropriate labels
            self.add_snippet(wp_creds, "WordPress Login")
            # self.add_snippet(instagram_creds, "Instagram Account")
            # self.add_snippet(facebook_creds, "Facebook Page")
            # self.add_snippet(email_creds, "Email Configuration")
            
            self.save_snippets()
            return
            
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    saved_snippets = json.load(f)
                
                if isinstance(saved_snippets, list):
                    if saved_snippets and isinstance(saved_snippets[0], dict):
                        # Load each snippet
                        for item in saved_snippets:
                            text = item.get("text", "")
                            label = item.get("label", "")
                            self.add_snippet(text, label)
                        
                        self.show_status(f"Loaded {len(saved_snippets)} saved snippets")
                    else:
                        # Handle old format without labels
                        for text_value in saved_snippets:
                            if isinstance(text_value, str):
                                self.add_snippet(text_value, "")
                            
                        self.show_status(f"Loaded {len(saved_snippets)} saved snippets (old format)")
            except json.JSONDecodeError:
                self.show_status("Error reading saved snippets file")
            except Exception as e:
                self.show_status(f"Error loading snippets: {str(e)}")
    
    def import_snippets(self):
        """Import snippets from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Snippets",
            "",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            # Determine file type from extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == ".json":
                # Import from JSON
                with open(file_path, "r") as f:
                    imported_data = json.load(f)
                
                # Clear existing snippets
                for snippet in self.snippets:
                    snippet["frame"].deleteLater()
                self.snippets.clear()
                
                # Add imported snippets
                if isinstance(imported_data, list):
                    if imported_data and isinstance(imported_data[0], dict):
                        # Import with labels
                        for item in imported_data:
                            text = item.get("text", "")
                            label = item.get("label", "")
                            self.add_snippet(text, label)
                    else:
                        # Import without labels
                        for text_value in imported_data:
                            self.add_snippet(text_value, "")
                
                self.show_status(f"Imported {len(imported_data)} snippets from JSON")
            else:
                # Import from text file (one snippet per line)
                with open(file_path, "r") as f:
                    lines = f.readlines()
                
                # Clear existing snippets
                for snippet in self.snippets:
                    snippet["frame"].deleteLater()
                self.snippets.clear()
                
                # Add imported snippets
                for line in lines:
                    self.add_snippet(line.strip(), "")
                
                self.show_status(f"Imported {len(lines)} snippets from text file")
            
            # Save the imported snippets
            self.save_snippets()
            
        except Exception as e:
            self.show_status(f"Import error: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Failed to import snippets: {str(e)}")
    
    def export_snippets(self, format_type="txt"):
        """Export snippets to a file."""
        if not self.snippets:
            self.show_status("No snippets to export")
            return
        
        # Determine file type and extension
        if format_type == "txt":
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        elif format_type == "html":
            file_filter = "HTML Files (*.html)"
            default_ext = ".html"
        elif format_type == "md":
            file_filter = "Markdown Files (*.md)"
            default_ext = ".md"
        else:
            file_filter = "All Files (*.*)"
            default_ext = ".txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Snippets",
            "",
            file_filter
        )
        
        if not file_path:
            return
        
        # Ensure the file has the correct extension
        if not file_path.endswith(default_ext):
            file_path += default_ext
        
        try:
            with open(file_path, "w") as f:
                if format_type == "txt":
                    # Plain text export
                    for snippet in self.snippets:
                        label = snippet["label_edit"].text()
                        text = snippet["text_edit"].toPlainText()
                        if label:
                            f.write(f"[{label}]\n{text}\n\n")
                        else:
                            f.write(f"{text}\n\n")
                
                elif format_type == "html":
                    # HTML export
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                    f.write("<title>Exported Snippets</title>\n")
                    f.write("<style>\n")
                    f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                    f.write(".snippet { border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; border-radius: 5px; }\n")
                    f.write(".label { font-weight: bold; color: #333; margin-bottom: 5px; }\n")
                    f.write(".text { white-space: pre-wrap; }\n")
                    f.write("</style>\n</head>\n<body>\n")
                    f.write(f"<h1>Exported Snippets</h1>\n")
                    f.write(f"<p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
                    
                    for i, snippet in enumerate(self.snippets, 1):
                        label = snippet["label_edit"].text()
                        text = snippet["text_edit"].toPlainText()
                        f.write(f'<div class="snippet">\n')
                        f.write(f'<div class="label">#{i}: {label}</div>\n')
                        f.write(f'<div class="text">{text}</div>\n')
                        f.write(f'</div>\n')
                    
                    f.write("</body>\n</html>")
                
                elif format_type == "md":
                    # Markdown export
                    f.write(f"# Exported Snippets\n\n")
                    f.write(f"Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for i, snippet in enumerate(self.snippets, 1):
                        label = snippet["label_edit"].text()
                        text = snippet["text_edit"].toPlainText()
                        f.write(f"## {i}. {label}\n\n")
                        f.write(f"```\n{text}\n```\n\n")
            
            self.show_status(f"Exported {len(self.snippets)} snippets to {format_type.upper()} file")
        
        except Exception as e:
            self.show_status(f"Export error: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Failed to export snippets: {str(e)}")
    
    def show_about_dialog(self):
        """Show information about the application."""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p>Version {VERSION}</p>
        <p>A powerful tool for managing and copying text snippets.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Save multiple text snippets</li>
            <li>Copy individual or all snippets</li>
            <li>Dark and light themes</li>
            <li>Import and export functionality</li>
            <li>Keyboard shortcuts</li>
            <li>Automatic persistence</li>
            <li>Rich text support (coming soon)</li>
            <li>Categories for organization (coming soon)</li>
        </ul>
        """
        
        QMessageBox.about(self, f"About {APP_NAME}", about_text)
    
    def show_shortcuts_dialog(self):
        """Display keyboard shortcuts information."""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
        <table>
            <tr><td><b>Ctrl+N</b></td><td>Clear all snippets</td></tr>
            <tr><td><b>Ctrl+O</b></td><td>Open/Import snippets</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>Save snippets</td></tr>
            <tr><td><b>Ctrl++</b></td><td>Add new snippet</td></tr>
            <tr><td><b>Ctrl+A</b></td><td>Copy all snippets</td></tr>
            <tr><td><b>Ctrl+D</b></td><td>Clear all snippets</td></tr>
            <tr><td><b>Ctrl+T</b></td><td>Toggle theme</td></tr>
            <tr><td><b>Alt+F4</b></td><td>Exit application</td></tr>
        </table>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setText(shortcuts_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Save snippets before closing
        self.save_snippets()
        event.accept()

    def apply_category_filter(self, index):
        """Filter snippets by selected category."""
        selected_category = self.category_filter.currentText()
        
        for snippet in self.snippets:
            snippet_category = snippet["label_edit"].text()
            frame = snippet["frame"]
            
            if selected_category == "All Categories" or snippet_category == selected_category:
                frame.setVisible(True)
            else:
                frame.setVisible(False)
    
    def search_snippets(self, search_text):
        """Search snippets by text content."""
        search_text = search_text.lower()
        
        for snippet in self.snippets:
            label = snippet["label_edit"].text().lower()
            content = snippet["text_edit"].toPlainText().lower()
            frame = snippet["frame"]
            
            if search_text in label or search_text in content:
                frame.setVisible(True)
            else:
                frame.setVisible(False)

    def toggle_snippet_expansion(self, text_edit):
        """Toggle a snippet between expanded and collapsed states."""
        # Find the snippet this text_edit belongs to
        for snippet in self.snippets:
            if snippet["text_edit"] == text_edit:
                # Toggle expanded state
                if snippet.get("is_expanded", False):
                    # Collapse
                    text_edit.setMinimumHeight(70)
                    text_edit.setMaximumHeight(70)
                    snippet["expand_btn"].setText("⬍")  # Down arrow
                    snippet["is_expanded"] = False
                else:
                    # Expand
                    text_edit.setMinimumHeight(70)
                    text_edit.setMaximumHeight(200)
                    snippet["expand_btn"].setText("⬆")  # Up arrow
                    snippet["is_expanded"] = True
                break

    def update_original_text(self, text_edit):
        """Update the original text when edited."""
        for snippet in self.snippets:
            if snippet["text_edit"] == text_edit:
                snippet["original_text"] = text_edit.toPlainText()
                break
    
    def mask_sensitive_data(self, text):
        """Replace sensitive data like passwords with asterisks."""
        # Find and mask passwords and tokens in the text
        masked_text = PASSWORD_PATTERN.sub(r'\1●●●●●●●●', text)
        return masked_text
    
    def toggle_sensitive_data(self, text_edit):
        """Toggle between masked and unmasked sensitive data."""
        for snippet in self.snippets:
            if snippet["text_edit"] == text_edit:
                if snippet.get("is_masked", False):
                    # Unmask - restore original text
                    text_edit.blockSignals(True)  # Prevent triggering textChanged
                    text_edit.setText(snippet["original_text"])
                    text_edit.blockSignals(False)
                    snippet["mask_btn"].setText("👁️")
                    snippet["is_masked"] = False
                    self.show_status("Sensitive data revealed")
                else:
                    # Mask - hide sensitive data
                    snippet["original_text"] = text_edit.toPlainText()
                    masked_text = self.mask_sensitive_data(snippet["original_text"])
                    text_edit.blockSignals(True)  # Prevent triggering textChanged
                    text_edit.setText(masked_text)
                    text_edit.blockSignals(False)
                    snippet["mask_btn"].setText("👁️‍🗨️")
                    snippet["is_masked"] = True
                    self.show_status("Sensitive data hidden")
                break
    
    def generate_password(self):
        """Generate a secure random password."""
        # Ask for password length
        length, ok = QInputDialog.getInt(
            self, "Password Length", 
            "Enter password length (8-64):",
            value=16, min=8, max=64
        )
        
        if not ok:
            return
            
        # Password character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?/"
        
        # Options for password
        use_uppercase, ok1 = QInputDialog.getItem(
            self, "Password Options",
            "Include uppercase letters?",
            ["Yes", "No"], 0, False
        )
        
        if not ok1:
            return
            
        use_digits, ok2 = QInputDialog.getItem(
            self, "Password Options",
            "Include numbers?",
            ["Yes", "No"], 0, False
        )
        
        if not ok2:
            return
            
        use_special, ok3 = QInputDialog.getItem(
            self, "Password Options",
            "Include special characters?",
            ["Yes", "No"], 0, False
        )
        
        if not ok3:
            return
        
        # Build character set based on options
        chars = lowercase
        if use_uppercase == "Yes":
            chars += uppercase
        if use_digits == "Yes":
            chars += digits
        if use_special == "Yes":
            chars += special
            
        # Generate password
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Copy to clipboard
        QApplication.clipboard().setText(password)
        
        # Show the password in a dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Generated Password")
        msg_box.setText(f"<b>Your new password:</b> {password}<br><br>The password has been copied to your clipboard.")
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Add buttons to create a new snippet with this password
        add_button = msg_box.addButton("Add as Snippet", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        
        msg_box.exec()
        
        # If "Add as Snippet" was clicked
        if msg_box.clickedButton() == add_button:
            # Ask for a label
            label, ok = QInputDialog.getText(
                self, "Snippet Label", 
                "Enter a label for this password:"
            )
            
            # Use "Password" as the default category if user didn't provide a label
            if ok:
                if not label:
                    label = "Password"
                self.add_snippet(f"Password: {password}", label)

def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    # Create and show the main window
    window = TextSnippetManager()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
