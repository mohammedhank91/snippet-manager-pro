"""
Main application window for the Snippet Manager Pro.
"""

import platform
import re
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QScrollArea, QFrame, 
    QMenu, QMenuBar, QStatusBar, QFileDialog, QDialog, 
    QTabWidget, QSplitter, QTextEdit, QComboBox, QCheckBox,
    QGridLayout, QToolBar, QToolButton, QMessageBox, 
    QSpacerItem, QSizePolicy, QInputDialog, QApplication,
    QListWidget, QListWidgetItem, QColorDialog
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from ..config import APP_NAME, VERSION, CATEGORY_COLORS
from ..utils import adjust_color, mask_sensitive_data, generate_password
from .snippet_widget import SnippetWidget
from ..database import SnippetDatabase

class MainWindow(QMainWindow):
    """Main application window for Text Snippet Manager Pro with PyQt6."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(f"{APP_NAME} by mohammedhank91")
        self.resize(800, 600)
        self.setMinimumSize(600, 400)
        
        # Application state
        self.is_dark_mode = False
        self.snippets = []
        self.current_theme = None
        self.database = SnippetDatabase()
        
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
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.show_status("Ready")
        
        # Initialize and apply theme
        self.toggle_theme()
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(lambda: self.add_snippet())
        file_menu.addAction(new_action)
        
        new_template_action = QAction("New &Template", self)
        new_template_action.setShortcut(QKeySequence("Ctrl+T"))
        new_template_action.triggered.connect(self.create_new_template)
        file_menu.addAction(new_template_action)
        
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
        add_action.triggered.connect(lambda: self.add_snippet())
        edit_menu.addAction(add_action)
        
        copy_all_action = QAction("&Copy All", self)
        copy_all_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        copy_all_action.triggered.connect(self.copy_all_snippets)
        edit_menu.addAction(copy_all_action)
        
        bulk_action = QAction("&Bulk Operations", self)
        bulk_action.triggered.connect(lambda: self.selection_mode_check.setChecked(True))
        edit_menu.addAction(bulk_action)
        
        clear_all_action = QAction("Clear &All", self)
        clear_all_action.setShortcut(QKeySequence("Ctrl+D"))
        clear_all_action.triggered.connect(self.clear_all_snippets)
        edit_menu.addAction(clear_all_action)
        
        # View menu
        view_menu = QMenu("&View", self)
        self.menu_bar.addMenu(view_menu)
        
        toggle_theme_action = QAction("Toggle &Dark Mode", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # Tools menu
        tools_menu = QMenu("&Tools", self)
        self.menu_bar.addMenu(tools_menu)
        
        password_action = QAction("&Generate Password", self)
        password_action.setShortcut(QKeySequence("Ctrl+G"))
        password_action.triggered.connect(self.generate_password_ui)
        tools_menu.addAction(password_action)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        self.menu_bar.addMenu(help_menu)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)
        
        markdown_help_action = QAction("&Markdown Help", self)
        markdown_help_action.triggered.connect(self.show_markdown_help)
        help_menu.addAction(markdown_help_action)
        
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
        password_gen_btn.clicked.connect(self.generate_password_ui)
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
    
    def create_tabs(self):
        """Create the tab widget with different views."""
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Create snippets tab
        self.snippets_tab = QWidget()
        self.tabs.addTab(self.snippets_tab, "Snippets")
        
        # Create categories tab
        self.categories_tab = QWidget()
        self.tabs.addTab(self.categories_tab, "Categories")
        
        # Create templates tab
        self.templates_tab = QWidget()
        self.tabs.addTab(self.templates_tab, "Templates")
        
        # Create settings tab
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        
        # Set up tabs
        self.setup_snippets_tab()
        self.setup_categories_tab()
        self.setup_templates_tab()
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
        
        # Add bulk operations menu
        bulk_layout = QHBoxLayout()
        bulk_label = QLabel("Bulk Operations:")
        bulk_layout.addWidget(bulk_label)
        
        # Selection mode toggle
        self.selection_mode_check = QCheckBox("Selection Mode")
        self.selection_mode_check.toggled.connect(self.toggle_selection_mode)
        bulk_layout.addWidget(self.selection_mode_check)
        
        # Add bulk actions button
        self.bulk_actions_btn = QPushButton("Bulk Actions")
        self.bulk_actions_btn.setEnabled(False)
        self.bulk_actions_btn.clicked.connect(self.show_bulk_actions_menu)
        bulk_layout.addWidget(self.bulk_actions_btn)
        
        # Selected count label
        self.selected_count_label = QLabel("0 selected")
        bulk_layout.addWidget(self.selected_count_label)
        
        bulk_layout.addStretch()
        snippets_layout.addLayout(bulk_layout)
        
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
        """Set up the categories tab for organizing and managing snippet categories."""
        categories_layout = QVBoxLayout(self.categories_tab)
        
        # Header section
        header_layout = QHBoxLayout()
        category_label = QLabel("Manage Snippet Categories")
        category_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(category_label)
        header_layout.addStretch()
        
        # Add new category button
        add_category_btn = QPushButton("Add Category")
        add_category_btn.clicked.connect(self.add_new_category)
        header_layout.addWidget(add_category_btn)
        
        categories_layout.addLayout(header_layout)
        
        # Description
        description = QLabel("Categories help you organize your snippets by topic. Each category can have its own color.")
        description.setWordWrap(True)
        categories_layout.addWidget(description)
        
        # Split view with categories list and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Categories list panel
        list_panel = QFrame()
        list_panel.setFrameShape(QFrame.Shape.StyledPanel)
        list_layout = QVBoxLayout(list_panel)
        
        list_header = QLabel("Current Categories:")
        list_layout.addWidget(list_header)
        
        self.categories_list = QListWidget()
        self.categories_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.categories_list.currentRowChanged.connect(self.on_category_selected)
        list_layout.addWidget(self.categories_list)
        
        # Category control buttons
        category_buttons = QHBoxLayout()
        
        self.edit_category_btn = QPushButton("Edit")
        self.edit_category_btn.clicked.connect(self.edit_selected_category)
        self.edit_category_btn.setEnabled(False)
        category_buttons.addWidget(self.edit_category_btn)
        
        self.delete_category_btn = QPushButton("Delete")
        self.delete_category_btn.setStyleSheet(f"background-color: {self.current_theme['danger_color'] if self.current_theme else '#f44336'};")
        self.delete_category_btn.clicked.connect(self.delete_selected_category)
        self.delete_category_btn.setEnabled(False)
        category_buttons.addWidget(self.delete_category_btn)
        
        list_layout.addLayout(category_buttons)
        
        # Category editor panel
        editor_panel = QFrame()
        editor_panel.setFrameShape(QFrame.Shape.StyledPanel)
        editor_layout = QVBoxLayout(editor_panel)
        
        editor_header = QLabel("Category Editor")
        editor_header.setStyleSheet("font-size: 12pt; font-weight: bold;")
        editor_layout.addWidget(editor_header)
        
        # Category name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_layout.addWidget(name_label)
        
        self.category_name_edit = QLineEdit()
        self.category_name_edit.setPlaceholderText("Enter category name")
        name_layout.addWidget(self.category_name_edit)
        
        editor_layout.addLayout(name_layout)
        
        # Color selector
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        color_layout.addWidget(color_label)
        
        self.color_preview = QFrame()
        self.color_preview.setFrameShape(QFrame.Shape.Box)
        self.color_preview.setMinimumSize(24, 24)
        self.color_preview.setMaximumSize(24, 24)
        self.color_preview.setStyleSheet("background-color: #666666;")
        color_layout.addWidget(self.color_preview)
        
        select_color_btn = QPushButton("Select Color")
        select_color_btn.clicked.connect(self.select_category_color)
        color_layout.addWidget(select_color_btn)
        
        color_layout.addStretch()
        editor_layout.addLayout(color_layout)
        
        # Assigned snippets section
        assigned_label = QLabel("Snippets with this category:")
        editor_layout.addWidget(assigned_label)
        
        self.assigned_snippets_list = QListWidget()
        editor_layout.addWidget(self.assigned_snippets_list)
        
        # Save and cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_category_edit)
        button_layout.addWidget(cancel_btn)
        
        self.save_category_btn = QPushButton("Save Category")
        self.save_category_btn.clicked.connect(self.save_category)
        button_layout.addWidget(self.save_category_btn)
        
        editor_layout.addLayout(button_layout)
        editor_layout.addStretch()
        
        # Add panels to splitter
        splitter.addWidget(list_panel)
        splitter.addWidget(editor_panel)
        splitter.setSizes([200, 400])
        
        categories_layout.addWidget(splitter, 1)
        
        # Initialize with current categories
        self.refresh_categories_list()
        self.clear_category_editor()
    
    def setup_templates_tab(self):
        """Set up the templates tab to view and manage template snippets."""
        templates_layout = QVBoxLayout(self.templates_tab)
        
        # Header section
        header_layout = QHBoxLayout()
        templates_label = QLabel("Snippet Templates")
        templates_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        header_layout.addWidget(templates_label)
        
        # Add new template button
        self.add_template_btn = QPushButton("Create New Template")
        self.add_template_btn.clicked.connect(self.create_new_template)
        header_layout.addWidget(self.add_template_btn)
        
        header_layout.addStretch()
        templates_layout.addLayout(header_layout)
        
        # Description
        description = QLabel(
            "Templates allow you to create reusable snippet structures. "
            "Mark any snippet as a template to make it available here."
        )
        description.setWordWrap(True)
        templates_layout.addWidget(description)
        
        # Create scroll area for templates
        self.templates_scroll = QScrollArea()
        self.templates_scroll.setWidgetResizable(True)
        self.templates_scroll.setFrameShape(QFrame.Shape.NoFrame)
        templates_layout.addWidget(self.templates_scroll)
        
        # Container for templates
        self.templates_container = QWidget()
        self.templates_scroll.setWidget(self.templates_container)
        
        # Layout for template listing
        self.templates_list_layout = QVBoxLayout(self.templates_container)
        self.templates_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.templates_list_layout.setContentsMargins(0, 0, 0, 0)
        self.templates_list_layout.setSpacing(10)
        
        # No templates label (shown when empty)
        self.no_templates_label = QLabel("No templates available. Mark any snippet as a template to see it here.")
        self.no_templates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_templates_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        self.templates_list_layout.addWidget(self.no_templates_label)
    
    def refresh_templates_tab(self):
        """Refresh the templates tab content based on current templates."""
        # Clear current templates
        for i in reversed(range(self.templates_list_layout.count())):
            widget = self.templates_list_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Get all template snippets
        templates = self.database.get_template_snippets()
        
        if not templates:
            # Show no templates message
            self.no_templates_label = QLabel("No templates available. Mark any snippet as a template to see it here.")
            self.no_templates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.no_templates_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.templates_list_layout.addWidget(self.no_templates_label)
            return
        
        # Add template widgets
        for template in templates:
            template_widget = self.create_template_widget(template)
            self.templates_list_layout.addWidget(template_widget)
    
    def create_template_widget(self, template_data):
        """Create a widget to display a template in the templates tab."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setLineWidth(1)
        
        # Apply theme
        secondary_bg = self.current_theme.get("secondary_bg", "#ffffff")
        frame.setStyleSheet(f"""
            QFrame {{
                border-left: 5px solid #4caf50;
                background-color: {secondary_bg};
                border-radius: 4px;
                margin-bottom: 5px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        
        # Template name/label
        header_layout = QHBoxLayout()
        label_text = template_data.get("label", "Untitled Template")
        label = QLabel(f"<b>{label_text}</b>")
        header_layout.addWidget(label)
        
        # Template tags display
        tags = template_data.get("tags", [])
        if tags:
            tags_text = ", ".join(tags)
            tags_label = QLabel(f"<i>Tags: {tags_text}</i>")
            tags_label.setStyleSheet("color: #0277bd;")
            header_layout.addWidget(tags_label)
        
        header_layout.addStretch()
        
        # Add "Use Template" button
        use_btn = QPushButton("Use Template")
        use_btn.clicked.connect(lambda: self.use_template(template_data.get("text", "")))
        header_layout.addWidget(use_btn)
        
        layout.addLayout(header_layout)
        
        # Template content preview
        text = template_data.get("text", "")
        preview_text = text[:150] + "..." if len(text) > 150 else text
        preview = QLabel(preview_text)
        preview.setWordWrap(True)
        preview.setStyleSheet("""
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px;
            font-family: monospace;
        """)
        layout.addWidget(preview)
        
        # If it's markdown, mention that
        if template_data.get("is_markdown", False):
            md_label = QLabel("Markdown Template")
            md_label.setStyleSheet("color: #2979ff; font-style: italic;")
            layout.addWidget(md_label)
        
        return frame
    
    def create_new_template(self):
        """Create a new blank template snippet."""
        # Create a new empty snippet with template flag set
        snippet = self.add_snippet("", "New Template", [], True, True)
        
        # Switch to the snippets tab for editing
        self.tabs.setCurrentIndex(0)
        
        # Focus the new snippet
        snippet.label_edit.setFocus()
        
        self.show_status("Created new template. Edit the content and it will appear in Templates tab.")
        
    def use_template(self, template_text):
        """Apply a template by creating a new snippet with the template text."""
        # Create a new snippet with the template text
        snippet = self.add_snippet(template_text, "From Template")
        
        # Switch to the snippets tab for editing if needed
        self.tabs.setCurrentIndex(0)
        
        # Focus the new snippet
        snippet.text_edit.setFocus()
        
        self.show_status("Created new snippet from template.")
    
    def on_tab_changed(self, index):
        """Handle tab change events."""
        # Refresh templates tab when switching to it
        if index == 2:  # Templates tab index
            self.refresh_templates_tab()
    
    def refresh_categories_list(self):
        """Update the categories list with current categories."""
        self.categories_list.clear()
        
        # Ensure 'default' category exists in CATEGORY_COLORS
        from ..config import CATEGORY_COLORS
        if "default" not in CATEGORY_COLORS:
            CATEGORY_COLORS["default"] = "#666666"  # Default gray
        
        # Add default category
        default_item = QListWidgetItem("default")
        default_item.setData(Qt.ItemDataRole.UserRole, {"name": "default", "color": CATEGORY_COLORS["default"]})
        self.categories_list.addItem(default_item)
        
        # Add all other categories from CATEGORY_COLORS
        for name, color in CATEGORY_COLORS.items():
            if name != "default":
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, {"name": name, "color": color})
                self.categories_list.addItem(item)
        
        # Update the category filter in the snippets tab
        self.update_category_filter()
    
    def update_category_filter(self):
        """Update the category filter dropdown in the snippets tab."""
        current_text = self.category_filter.currentText()
        self.category_filter.clear()
        
        # Add default "All Categories" option
        self.category_filter.addItem("All Categories")
        
        # Add each category
        for name in CATEGORY_COLORS.keys():
            self.category_filter.addItem(name)
        
        # Try to restore the previous selection
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)
    
    def on_category_selected(self, row):
        """Handle selection of a category in the list."""
        if row >= 0:
            self.edit_category_btn.setEnabled(True)
            self.delete_category_btn.setEnabled(row > 0)  # Disable delete for default category
            
            # Display category info
            item = self.categories_list.item(row)
            category_data = item.data(Qt.ItemDataRole.UserRole)
            
            self.category_name_edit.setText(category_data["name"])
            self.color_preview.setStyleSheet(f"background-color: {category_data['color']};")
            
            # Show snippets with this category
            self.update_assigned_snippets(category_data["name"])
        else:
            self.edit_category_btn.setEnabled(False)
            self.delete_category_btn.setEnabled(False)
            self.clear_category_editor()
    
    def update_assigned_snippets(self, category_name):
        """Update the list of snippets assigned to the selected category."""
        self.assigned_snippets_list.clear()
        
        # Count snippets with this category
        count = 0
        for snippet in self.snippets:
            if snippet.get_label() == category_name:
                count += 1
                # Add snippet text preview (truncated if too long)
                text = snippet.get_text()
                preview = text[:40] + "..." if len(text) > 40 else text
                self.assigned_snippets_list.addItem(preview)
        
        # If no snippets, show a message
        if count == 0:
            self.assigned_snippets_list.addItem("No snippets with this category.")
    
    def clear_category_editor(self):
        """Clear the category editor fields."""
        self.category_name_edit.clear()
        self.color_preview.setStyleSheet("background-color: #666666;")
        self.assigned_snippets_list.clear()
    
    def add_new_category(self):
        """Add a new category."""
        self.clear_category_editor()
        self.categories_list.clearSelection()
        self.color_preview.setStyleSheet("background-color: #666666;")
        
        # Enable the editor for a new category
        self.category_name_edit.setFocus()
    
    def edit_selected_category(self):
        """Edit the currently selected category."""
        row = self.categories_list.currentRow()
        if row >= 0:
            item = self.categories_list.item(row)
            category_data = item.data(Qt.ItemDataRole.UserRole)
            
            self.category_name_edit.setText(category_data["name"])
            self.color_preview.setStyleSheet(f"background-color: {category_data['color']};")
            self.category_name_edit.setFocus()
    
    def delete_selected_category(self):
        """Delete the currently selected category."""
        row = self.categories_list.currentRow()
        if row > 0:  # Don't allow deleting the default category
            item = self.categories_list.item(row)
            category_name = item.data(Qt.ItemDataRole.UserRole)["name"]
            
            # Confirm deletion
            confirm = QMessageBox.question(
                self, 
                "Delete Category",
                f"Are you sure you want to delete the category '{category_name}'?\n\n"
                "Snippets with this category will be reassigned to 'default'.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Reassign snippets to default category
                for snippet in self.snippets:
                    if snippet.get_label() == category_name:
                        snippet.set_label("default")
                
                # Remove from CATEGORY_COLORS
                if category_name in CATEGORY_COLORS:
                    del CATEGORY_COLORS[category_name]
                
                # Refresh UI
                self.refresh_categories_list()
                self.clear_category_editor()
                
                # Save changes
                self.save_snippets()
                self.show_status(f"Category '{category_name}' deleted")
    
    def select_category_color(self):
        """Open color picker to select a category color."""
        current_color = self.color_preview.palette().color(self.color_preview.backgroundRole())
        color = QColorDialog.getColor(current_color, self, "Select Category Color")
        
        if color.isValid():
            self.color_preview.setStyleSheet(f"background-color: {color.name()};")
    
    def cancel_category_edit(self):
        """Cancel editing a category."""
        self.clear_category_editor()
        self.categories_list.clearSelection()
    
    def save_category(self):
        """Save the current category."""
        name = self.category_name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Invalid Category", "Category name cannot be empty.")
            return
        
        # Extract color from stylesheet
        style = self.color_preview.styleSheet()
        color_match = re.search(r'background-color:\s*(#[0-9a-fA-F]{6})', style)
        color = color_match.group(1) if color_match else "#666666"
        
        # Check if editing existing category
        row = self.categories_list.currentRow()
        old_name = None
        if row >= 0:
            item = self.categories_list.item(row)
            old_name = item.data(Qt.ItemDataRole.UserRole)["name"]
        
        # Update category colors
        if old_name and old_name != name:
            # Rename: remove old and add new
            if old_name in CATEGORY_COLORS:
                color_value = CATEGORY_COLORS[old_name]
                del CATEGORY_COLORS[old_name]
                CATEGORY_COLORS[name] = color
                
                # Update snippets with this category
                for snippet in self.snippets:
                    if snippet.get_label() == old_name:
                        snippet.set_label(name)
            else:
                CATEGORY_COLORS[name] = color
        else:
            # New category or updating color only
            CATEGORY_COLORS[name] = color
        
        # Refresh UI
        self.refresh_categories_list()
        self.clear_category_editor()
        
        # Save changes
        self.save_snippets()
        
        action = "updated" if old_name else "added"
        self.show_status(f"Category '{name}' {action}")
    
    def on_theme_selected(self, index):
        """Handle theme selection from the dropdown."""
        self.is_dark_mode = (index == 1)
        self.toggle_theme()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        from ..config import DARK_THEME, LIGHT_THEME
        
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
                background-color: {adjust_color(accent_color, 20, self.is_dark_mode)};
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
                background-color: {adjust_color(bg_color, 20, self.is_dark_mode)};
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
            snippet.apply_theme(self.current_theme, self.is_dark_mode)
    
    def show_status(self, message, timeout=3000):
        """Display a message in the status bar."""
        self.status_bar.showMessage(message, timeout)
    
    def add_snippet(self, text="", label="", tags=None, is_markdown=False, is_template=False):
        """Add a new snippet to the collection."""
        # Create a new snippet widget
        row_num = len(self.snippets) + 1
        snippet = SnippetWidget(text, label, row_num, self.current_theme, self.is_dark_mode)
        
        # Set additional properties
        if tags:
            snippet.set_tags(tags)
        
        snippet.set_markdown_enabled(is_markdown)
        snippet.set_template_enabled(is_template)
        
        # Connect signals
        snippet.delete_requested.connect(self.delete_snippet)
        snippet.content_changed.connect(self.on_snippet_changed)
        snippet.copy_requested.connect(self.copy_snippet_text)
        snippet.tag_added.connect(self.on_tag_added)
        snippet.tag_removed.connect(self.on_tag_removed)
        snippet.apply_template.connect(self.use_template)
        snippet.selection_changed.connect(self.update_selected_count)
        
        # Add to UI and internal list
        self.snippets_layout.addWidget(snippet)
        self.snippets.append(snippet)
        
        # Update row numbers
        self.update_row_numbers()
        
        # Add category to filter if it's not already there
        if label and self.category_filter.findText(label) == -1:
            self.category_filter.addItem(label)
        
        self.show_status(f"Added new snippet #{row_num}")
        return snippet
    
    def update_row_numbers(self):
        """Update the row numbers after deletion or addition."""
        for i, snippet in enumerate(self.snippets, 1):
            snippet.set_row_number(i)
    
    def delete_snippet(self, snippet):
        """Delete a snippet from the collection."""
        if snippet in self.snippets:
            row_num = snippet.row_num
            self.snippets.remove(snippet)
            snippet.deleteLater()
            self.update_row_numbers()
            
            # Save changes if auto-save is enabled
            if self.auto_save_checkbox.isChecked():
                self.save_snippets()
                
            self.show_status(f"Deleted snippet #{row_num}")
    
    def copy_snippet_text(self, text):
        """Copy snippet text to clipboard and show status."""
        if text:
            QApplication.clipboard().setText(text)
            self.show_status(f"Copied: {text[:30]}{'...' if len(text) > 30 else ''}")
        else:
            self.show_status("Nothing to copy - snippet is empty!")
    
    def copy_all_snippets(self):
        """Copy all snippet texts concatenated to the clipboard."""
        all_texts = "\n".join(snippet.get_text() for snippet in self.snippets 
                             if snippet.get_text().strip())
        
        if all_texts:
            QApplication.clipboard().setText(all_texts)
            count = sum(1 for snippet in self.snippets 
                      if snippet.get_text().strip())
            self.show_status(f"Copied all {count} snippets to clipboard")
        else:
            self.show_status("Nothing to copy - all snippets are empty!")
    
    def clear_all_snippets(self):
        """Clear all snippets and add one empty snippet."""
        if self.snippets:
            for snippet in self.snippets:
                snippet.deleteLater()
            
            count = len(self.snippets)
            self.snippets.clear()
            self.add_snippet()
            
            # Save changes if auto-save is enabled
            if self.auto_save_checkbox.isChecked():
                self.save_snippets()
            
            self.show_status(f"Cleared all {count} snippets")
        else:
            self.show_status("No snippets to clear")
    
    def on_snippet_changed(self):
        """Handle when a snippet's content changes."""
        # Flag snippets as modified
        self.snippets_modified = True
        self.save_snippets()

    def on_tag_added(self, tag):
        """Handle when a tag is added to a snippet."""
        # Save when tags are modified
        self.snippets_modified = True
        self.save_snippets()
        
        # Refresh tag lists if needed
        if hasattr(self, 'tag_filter_combo'):
            self.refresh_tag_filter()

    def on_tag_removed(self, tag):
        """Handle when a tag is removed from a snippet."""
        # Save when tags are modified
        self.snippets_modified = True
        self.save_snippets()
        
        # Refresh tag lists if needed
        if hasattr(self, 'tag_filter_combo'):
            self.refresh_tag_filter()
        
    def refresh_tag_filter(self):
        """Refresh the tag filter dropdown with all available tags."""
        if hasattr(self, 'tag_filter_combo'):
            # Store current selection
            current_selection = self.tag_filter_combo.currentText()
            
            # Get all tags from database
            all_tags = self.database.get_all_tags()
            
            # Update combo box
            self.tag_filter_combo.clear()
            self.tag_filter_combo.addItem("All Tags")
            for tag in all_tags:
                self.tag_filter_combo.addItem(tag)
            
            # Restore selection if possible
            index = self.tag_filter_combo.findText(current_selection)
            if index >= 0:
                self.tag_filter_combo.setCurrentIndex(index)

    def save_snippets(self):
        """Save all snippets to the JSON file."""
        snippets_data = []
        
        for snippet in self.snippets:
            snippets_data.append(snippet.get_snippet_data())
        
        success, message = self.database.save_snippets(snippets_data)
        if success:
            self.show_status(message)
        else:
            self.show_status(message)
            QMessageBox.warning(self, "Save Error", message)
    
    def load_snippets(self):
        """Load snippets from the JSON file."""
        saved_snippets, message = self.database.load_snippets()
        
        # Clear any existing snippets
        for snippet in self.snippets:
            snippet.deleteLater()
        self.snippets.clear()
        
        # Add loaded snippets
        if saved_snippets:
            for item in saved_snippets:
                text = item.get("text", "")
                label = item.get("label", "")
                tags = item.get("tags", [])
                is_markdown = item.get("is_markdown", False)
                is_template = item.get("is_template", False)
                
                self.add_snippet(text, label, tags, is_markdown, is_template)
        else:
            # Add an empty snippet if none were loaded
            self.add_snippet()
        
        self.show_status(message)
    
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
            
        imported_snippets, message = self.database.import_from_file(file_path)
        
        if imported_snippets:
            # Clear existing snippets
            for snippet in self.snippets:
                snippet.deleteLater()
            self.snippets.clear()
            
            # Add imported snippets
            for item in imported_snippets:
                text = item.get("text", "")
                label = item.get("label", "")
                self.add_snippet(text, label)
            
            # Save the imported snippets
            self.save_snippets()
            
            self.show_status(message)
        else:
            self.show_status(message)
            QMessageBox.critical(self, "Import Error", message)
    
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
        
        # Convert snippets to data format for export
        snippets_data = []
        for snippet in self.snippets:
            snippets_data.append(snippet.get_snippet_data())
        
        success, message = self.database.export_to_file(snippets_data, file_path, format_type)
        if success:
            self.show_status(message)
        else:
            self.show_status(message)
            QMessageBox.critical(self, "Export Error", message)
    
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
        <p>Developed by <a href="https://github.com/mohammedhank91">mohammedhank91</a></p>
        <p><a href="https://github.com/mohammedhank91/snippet-manager-pro">GitHub Repository</a></p>
        """
        
        QMessageBox.about(self, f"About {APP_NAME}", about_text)
    
    def show_shortcuts_dialog(self):
        """Display keyboard shortcuts information."""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>
        <table>
            <tr><td><b>Ctrl+N</b></td><td>New snippet</td></tr>
            <tr><td><b>Ctrl+T</b></td><td>New template</td></tr>
            <tr><td><b>Ctrl+O</b></td><td>Open/Import snippets</td></tr>
            <tr><td><b>Ctrl+S</b></td><td>Save snippets</td></tr>
            <tr><td><b>Ctrl++</b></td><td>Add new snippet</td></tr>
            <tr><td><b>Ctrl+Shift+C</b></td><td>Copy all snippets</td></tr>
            <tr><td><b>Ctrl+D</b></td><td>Clear all snippets</td></tr>
            <tr><td><b>Ctrl+Shift+D</b></td><td>Toggle dark mode</td></tr>
            <tr><td><b>Ctrl+G</b></td><td>Generate password</td></tr>
            <tr><td><b>Alt+F4</b></td><td>Exit application</td></tr>
        </table>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setText(shortcuts_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
    
    def apply_category_filter(self, index):
        """Filter snippets by selected category."""
        selected_category = self.category_filter.currentText()
        
        for snippet in self.snippets:
            snippet_category = snippet.get_label()
            
            if selected_category == "All Categories" or snippet_category == selected_category:
                snippet.setVisible(True)
            else:
                snippet.setVisible(False)
    
    def search_snippets(self, search_text):
        """Search snippets by text content."""
        search_text = search_text.lower()
        
        for snippet in self.snippets:
            label = snippet.get_label().lower()
            content = snippet.get_text().lower()
            
            if search_text in label or search_text in content:
                snippet.setVisible(True)
            else:
                snippet.setVisible(False)
    
    def generate_password_ui(self):
        """Generate a password with UI interaction."""
        # Ask for password length
        length, ok = QInputDialog.getInt(
            self, "Password Length", 
            "Enter password length (8-64):",
            value=16, min=8, max=64
        )
        
        if not ok:
            return
            
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
        
        # Generate password
        password = generate_password(
            length=length,
            use_uppercase=(use_uppercase == "Yes"),
            use_digits=(use_digits == "Yes"),
            use_special=(use_special == "Yes")
        )
        
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
            
            if ok:
                if not label:
                    label = "Password"
                self.add_snippet(f"Password: {password}", label, ["password", "security"], False, False)
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Save snippets before closing
        self.save_snippets()
        event.accept()
    
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
        
        github_label = QLabel(f'Developed by <a href="https://github.com/mohammedhank91">mohammedhank91</a>')
        github_label.setOpenExternalLinks(True)
        about_layout.addWidget(github_label)
        
        settings_layout.addWidget(about_group)
        
        # Add spacer to push everything to the top
        settings_layout.addStretch()
    
    def toggle_selection_mode(self, enabled):
        """Toggle snippet selection mode for bulk operations."""
        for snippet in self.snippets:
            snippet.set_selection_mode(enabled)
        
        self.bulk_actions_btn.setEnabled(enabled)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Update the selected snippets count label."""
        count = sum(1 for snippet in self.snippets if snippet.is_selected())
        self.selected_count_label.setText(f"{count} selected")
        
        # Enable/disable bulk actions button based on selection
        self.bulk_actions_btn.setEnabled(count > 0)
    
    def show_bulk_actions_menu(self):
        """Show the bulk actions context menu."""
        if not any(snippet.is_selected() for snippet in self.snippets):
            QMessageBox.information(self, "No Selection", "Please select at least one snippet for bulk operations.")
            return
            
        menu = QMenu(self)
        
        # Delete selected snippets
        delete_action = QAction("Delete Selected", self)
        delete_action.triggered.connect(self.delete_selected_snippets)
        menu.addAction(delete_action)
        
        # Export selected snippets
        export_menu = QMenu("Export Selected", menu)
        
        export_txt_action = QAction("Export as Text", self)
        export_txt_action.triggered.connect(lambda: self.export_selected_snippets("txt"))
        export_menu.addAction(export_txt_action)
        
        export_html_action = QAction("Export as HTML", self)
        export_html_action.triggered.connect(lambda: self.export_selected_snippets("html"))
        export_menu.addAction(export_html_action)
        
        export_md_action = QAction("Export as Markdown", self)
        export_md_action.triggered.connect(lambda: self.export_selected_snippets("md"))
        export_menu.addAction(export_md_action)
        
        menu.addMenu(export_menu)
        
        # Category operations
        category_menu = QMenu("Change Category", menu)
        
        # Add all categories
        for category in CATEGORY_COLORS.keys():
            action = QAction(category, self)
            action.triggered.connect(lambda checked, c=category: self.change_selected_category(c))
            category_menu.addAction(action)
        
        menu.addMenu(category_menu)
        
        # Tag operations
        tag_menu = QMenu("Tag Operations", menu)
        
        add_tag_action = QAction("Add Tag...", self)
        add_tag_action.triggered.connect(self.add_tag_to_selected)
        tag_menu.addAction(add_tag_action)
        
        remove_tag_action = QAction("Remove Tag...", self)
        remove_tag_action.triggered.connect(self.remove_tag_from_selected)
        tag_menu.addAction(remove_tag_action)
        
        menu.addMenu(tag_menu)
        
        # Template/Markdown operations
        format_menu = QMenu("Format Options", menu)
        
        toggle_markdown_action = QAction("Toggle Markdown", self)
        toggle_markdown_action.triggered.connect(self.toggle_selected_markdown)
        format_menu.addAction(toggle_markdown_action)
        
        toggle_template_action = QAction("Toggle Template", self)
        toggle_template_action.triggered.connect(self.toggle_selected_template)
        format_menu.addAction(toggle_template_action)
        
        menu.addMenu(format_menu)
        
        # Show the menu
        menu.exec(self.bulk_actions_btn.mapToGlobal(self.bulk_actions_btn.rect().bottomLeft()))
    
    def get_selected_snippet_indices(self):
        """Get the indices of selected snippets."""
        return [i for i, snippet in enumerate(self.snippets) if snippet.is_selected()]
    
    def delete_selected_snippets(self):
        """Delete all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        confirm = QMessageBox.question(
            self, 
            "Delete Snippets",
            f"Are you sure you want to delete {len(selected_indices)} snippets?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Use the bulk delete function from database
            success, message = self.database.bulk_delete_snippets(selected_indices)
            
            if success:
                # Turn off selection mode
                self.selection_mode_check.setChecked(False)
                
                # Reload snippets to reflect changes
                self.load_snippets()
                
                self.show_status(message)
            else:
                QMessageBox.warning(self, "Delete Error", message)
    
    def export_selected_snippets(self, format_type):
        """Export only the selected snippets to a file."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
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
            f"Export {len(selected_indices)} Snippets",
            "",
            file_filter
        )
        
        if not file_path:
            return
            
        # Ensure the file has the correct extension
        if not file_path.endswith(default_ext):
            file_path += default_ext
            
        # Get all snippets
        snippets, _ = self.database.load_snippets()
        
        # Filter to only selected snippets
        selected_snippets = [snippets[i] for i in selected_indices if i < len(snippets)]
        
        # Export only selected snippets
        success, message = self.database.export_to_file(selected_snippets, file_path, format_type)
        
        if success:
            self.show_status(message)
        else:
            QMessageBox.warning(self, "Export Error", message)
    
    def change_selected_category(self, category):
        """Change the category of all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        # Use bulk update with the new category
        success, message = self.database.bulk_update_snippets(selected_indices, {"label": category})
        
        if success:
            # Update UI to reflect changes
            for i in selected_indices:
                if i < len(self.snippets):
                    self.snippets[i].set_label(category)
                    
            self.show_status(message)
        else:
            QMessageBox.warning(self, "Update Error", message)
    
    def add_tag_to_selected(self):
        """Add a tag to all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        # Get all current tags for auto-complete
        all_tags = self.database.get_all_tags()
        
        # Show tag input dialog
        tag, ok = QInputDialog.getText(
            self, 
            "Add Tag", 
            f"Enter tag to add to {len(selected_indices)} snippets:",
            QLineEdit.EchoMode.Normal
        )
        
        if ok and tag:
            # Load all snippets to update them
            snippets, _ = self.database.load_snippets()
            
            # Update tag for each selected snippet
            for idx in selected_indices:
                if idx < len(snippets):
                    tags = snippets[idx].get("tags", [])
                    if tag not in tags:
                        tags.append(tag)
                    snippets[idx]["tags"] = tags
            
            # Save the updated snippets
            success, message = self.database.save_snippets(snippets)
            
            if success:
                # Update UI to reflect changes
                for i in selected_indices:
                    if i < len(self.snippets):
                        self.snippets[i].add_tag(tag)
                        
                self.show_status(f"Added tag '{tag}' to {len(selected_indices)} snippets")
            else:
                QMessageBox.warning(self, "Update Error", message)
    
    def remove_tag_from_selected(self):
        """Remove a tag from all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        # Get all currently used tags
        all_tags = set()
        for i in selected_indices:
            if i < len(self.snippets):
                all_tags.update(self.snippets[i].get_tags())
                
        if not all_tags:
            QMessageBox.information(self, "No Tags", "The selected snippets don't have any tags to remove.")
            return
                
        # Show tag selection dialog
        tag, ok = QInputDialog.getItem(
            self, 
            "Remove Tag", 
            f"Select tag to remove from {len(selected_indices)} snippets:",
            sorted(list(all_tags)),
            0,  # Current item
            False  # Not editable
        )
        
        if ok and tag:
            # Load all snippets to update them
            snippets, _ = self.database.load_snippets()
            
            # Update tag for each selected snippet
            for idx in selected_indices:
                if idx < len(snippets):
                    tags = snippets[idx].get("tags", [])
                    if tag in tags:
                        tags.remove(tag)
                    snippets[idx]["tags"] = tags
            
            # Save the updated snippets
            success, message = self.database.save_snippets(snippets)
            
            if success:
                # Update UI to reflect changes
                for i in selected_indices:
                    if i < len(self.snippets):
                        self.snippets[i].remove_tag(tag)
                        
                self.show_status(f"Removed tag '{tag}' from {len(selected_indices)} snippets")
            else:
                QMessageBox.warning(self, "Update Error", message)
    
    def toggle_selected_markdown(self):
        """Toggle markdown status for all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        # Determine the new state - we'll use the opposite of the majority
        md_count = sum(1 for i in selected_indices if i < len(self.snippets) and self.snippets[i].is_markdown_enabled())
        new_state = md_count <= len(selected_indices) / 2  # Set to True if less than half are currently markdown
        
        # Update all selected snippets
        success, message = self.database.bulk_update_snippets(selected_indices, {"is_markdown": new_state})
        
        if success:
            # Update UI to reflect changes
            for i in selected_indices:
                if i < len(self.snippets):
                    self.snippets[i].set_markdown_enabled(new_state)
                    
            state_str = "enabled" if new_state else "disabled"
            self.show_status(f"Markdown {state_str} for {len(selected_indices)} snippets")
        else:
            QMessageBox.warning(self, "Update Error", message)
    
    def toggle_selected_template(self):
        """Toggle template status for all selected snippets."""
        selected_indices = self.get_selected_snippet_indices()
        if not selected_indices:
            return
            
        # Determine the new state - we'll use the opposite of the majority
        template_count = sum(1 for i in selected_indices if i < len(self.snippets) and self.snippets[i].is_template_enabled())
        new_state = template_count <= len(selected_indices) / 2  # Set to True if less than half are currently templates
        
        # Update all selected snippets
        success, message = self.database.bulk_update_snippets(selected_indices, {"is_template": new_state})
        
        if success:
            # Update UI to reflect changes
            for i in selected_indices:
                if i < len(self.snippets):
                    self.snippets[i].set_template_enabled(new_state)
                    
            state_str = "enabled" if new_state else "disabled"
            self.show_status(f"Template {state_str} for {len(selected_indices)} snippets")
        else:
            QMessageBox.warning(self, "Update Error", message)
    
    def show_markdown_help(self):
        """Show help information about Markdown syntax."""
        help_text = """
        <h2>Markdown Syntax Guide</h2>
        
        <h3>Basic Syntax</h3>
        <table>
            <tr><td><b># Heading 1</b></td><td>Creates a level 1 heading</td></tr>
            <tr><td><b>## Heading 2</b></td><td>Creates a level 2 heading</td></tr>
            <tr><td><b>### Heading 3</b></td><td>Creates a level 3 heading</td></tr>
            <tr><td><b>**bold text**</b></td><td>Makes text <b>bold</b></td></tr>
            <tr><td><b>*italic text*</b></td><td>Makes text <i>italic</i></td></tr>
            <tr><td><b>[link text](URL)</b></td><td>Creates a hyperlink</td></tr>
            <tr><td><b>![alt text](image-url)</b></td><td>Embeds an image</td></tr>
            <tr><td><b>- Item 1<br>- Item 2</b></td><td>Creates an unordered list</td></tr>
            <tr><td><b>1. Item 1<br>2. Item 2</b></td><td>Creates an ordered list</td></tr>
            <tr><td><b>---</b></td><td>Creates a horizontal rule</td></tr>
            <tr><td><b>`code`</b></td><td>Formats text as <code>code</code></td></tr>
        </table>
        
        <h3>Extended Syntax</h3>
        <table>
            <tr><td><b>```<br>code block<br>```</b></td><td>Creates a code block</td></tr>
            <tr><td><b>> quote</b></td><td>Creates a blockquote</td></tr>
            <tr><td><b>- [x] Task</b></td><td>Creates a checked task</td></tr>
            <tr><td><b>- [ ] Task</b></td><td>Creates an unchecked task</td></tr>
            <tr><td><b>| Header | Header |<br>|--------|--------| <br>| Cell | Cell |</b></td><td>Creates a table</td></tr>
        </table>
        
        <p>Markdown can be enabled for any snippet by checking the "Markdown" checkbox.</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Markdown Help")
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec() 