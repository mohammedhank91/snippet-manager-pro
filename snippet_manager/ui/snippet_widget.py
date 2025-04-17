"""
Widget for displaying and managing individual snippets.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QPushButton, QLabel, QLineEdit, QTextEdit, QFrame,
    QSizePolicy, QMenu, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction

from ..config import CATEGORY_COLORS
from ..utils import mask_sensitive_data

# Import markdown if available for rendering
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

class TagLabel(QLabel):
    """A clickable tag label with remove capability."""
    
    remove_clicked = pyqtSignal(str)
    
    def __init__(self, tag_text, parent=None):
        """Initialize the tag label."""
        super().__init__(parent)
        self.tag_text = tag_text
        self.setText(f" {tag_text} ✕")
        self.setStyleSheet("""
            background-color: #e1f5fe;
            color: #0277bd;
            border-radius: 10px;
            padding: 2px 5px;
            margin: 2px;
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def mousePressEvent(self, event):
        """Handle mouse press event to remove the tag."""
        self.remove_clicked.emit(self.tag_text)
        super().mousePressEvent(event)

class SnippetWidget(QFrame):
    """Widget for an individual text snippet with editing capabilities."""
    
    # Custom signals
    delete_requested = pyqtSignal(object)
    content_changed = pyqtSignal()
    copy_requested = pyqtSignal(str)
    tag_added = pyqtSignal(str)
    tag_removed = pyqtSignal(str)
    apply_template = pyqtSignal(str)
    selection_changed = pyqtSignal()
    
    def __init__(self, text="", label="", row_num=1, theme=None, is_dark_mode=False):
        """Initialize the snippet widget with the given text and label."""
        super().__init__()
        
        self.row_num = row_num
        # Ignore boolean False values, converting other non-None values to strings
        self.text = "" if text is False else (str(text) if text is not None else "")
        self.label = str(label) if label is not None else ""
        self.is_expanded = False
        self.is_masked = False
        self.original_text = self.text
        self.theme = theme or {}
        self.is_dark_mode = is_dark_mode
        self.tags = []
        self.is_markdown = False
        self.is_template = False
        self.selection_mode = False
        self.selected = False
        
        # Set up the widget UI
        self.setup_ui()
        self.apply_theme(self.theme, self.is_dark_mode)
    
    def setup_ui(self):
        """Set up the widget UI components."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        # Create main layout
        self.snippet_layout = QGridLayout(self)
        self.snippet_layout.setContentsMargins(10, 10, 10, 10)
        self.snippet_layout.setVerticalSpacing(0)  # Remove spacing between rows
        
        # Header row
        header_layout = QHBoxLayout()
        
        # Add selection checkbox (hidden by default)
        self.select_checkbox = QCheckBox()
        self.select_checkbox.setHidden(True)
        self.select_checkbox.toggled.connect(self.on_selection_toggled)
        header_layout.addWidget(self.select_checkbox)
        
        # Add row number
        self.row_label = QLabel(f"{self.row_num}.")
        header_layout.addWidget(self.row_label)
        
        # Add label/description field
        self.label_edit = QLineEdit(self.label)
        self.label_edit.setPlaceholderText("Snippet Description")
        self.label_edit.textChanged.connect(self.on_label_changed)
        header_layout.addWidget(self.label_edit)
        
        header_layout.addStretch()
        
        # Add snippet type buttons
        self.type_btn_layout = QHBoxLayout()
        
        # Markdown toggle
        self.markdown_check = QCheckBox("Markdown")
        self.markdown_check.setChecked(self.is_markdown)
        self.markdown_check.toggled.connect(self.toggle_markdown)
        self.type_btn_layout.addWidget(self.markdown_check)
        
        # Template toggle
        self.template_check = QCheckBox("Template")
        self.template_check.setChecked(self.is_template)
        self.template_check.toggled.connect(self.toggle_template)
        self.type_btn_layout.addWidget(self.template_check)
        
        # Add expand/collapse button
        self.expand_btn = QPushButton("⬍")  # Down arrow Unicode character
        self.expand_btn.setToolTip("Expand/Collapse")
        self.expand_btn.setFixedWidth(30)
        self.expand_btn.clicked.connect(self.toggle_expansion)
        self.type_btn_layout.addWidget(self.expand_btn)
        
        # Add hide/show sensitive data button
        self.mask_btn = QPushButton("👁️")  # Eye Unicode character
        self.mask_btn.setToolTip("Hide/Show Sensitive Data")
        self.mask_btn.setFixedWidth(30)
        self.mask_btn.clicked.connect(self.toggle_sensitive_data)
        self.type_btn_layout.addWidget(self.mask_btn)
        
        header_layout.addLayout(self.type_btn_layout)
        
        self.snippet_layout.addLayout(header_layout, 0, 0, 1, 3)
        
        # Tags row
        self.tags_layout = QHBoxLayout()
        self.tags_label = QLabel("Tags:")
        self.tags_layout.addWidget(self.tags_label)
        
        # Container for tag labels
        self.tags_container = QWidget()
        self.tags_container_layout = QHBoxLayout(self.tags_container)
        self.tags_container_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_container_layout.setSpacing(2)
        self.tags_layout.addWidget(self.tags_container)
        
        # Add tag button
        self.add_tag_btn = QPushButton("+")
        self.add_tag_btn.setToolTip("Add Tag")
        self.add_tag_btn.setFixedWidth(25)
        self.add_tag_btn.clicked.connect(self.show_add_tag_menu)
        self.tags_layout.addWidget(self.add_tag_btn)
        
        self.tags_layout.addStretch()
        
        self.snippet_layout.addLayout(self.tags_layout, 1, 0, 1, 3)
        
        # Add text edit field
        self.text_edit = QTextEdit()
        self.text_edit.setText(self.text)
        self.text_edit.setAcceptRichText(False)
        self.text_edit.setPlaceholderText("Enter your snippet text here...")
        self.text_edit.setMinimumHeight(70)
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.snippet_layout.addWidget(self.text_edit, 2, 0, 1, 3)
        
        # Add markdown preview container (hidden by default)
        self.md_preview = QLabel()
        self.md_preview.setTextFormat(Qt.TextFormat.RichText)
        self.md_preview.setWordWrap(True)
        self.md_preview.setStyleSheet("""
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-top: 5px;
        """)
        self.md_preview.setHidden(True)
        self.snippet_layout.addWidget(self.md_preview, 3, 0, 1, 3)
        
        # Add snippet actions
        actions_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.clicked.connect(self.copy_text)
        actions_layout.addWidget(self.copy_btn)
        
        # Add Use Template button (hidden by default)
        self.use_template_btn = QPushButton("Use Template")
        self.use_template_btn.clicked.connect(self.use_as_template)
        self.use_template_btn.setHidden(True)
        actions_layout.addWidget(self.use_template_btn)
        
        actions_layout.addStretch()
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_snippet)
        actions_layout.addWidget(self.delete_btn)
        
        self.snippet_layout.addLayout(actions_layout, 4, 0, 1, 3)
    
    def apply_theme(self, theme, is_dark_mode):
        """Apply the theme to the snippet widget."""
        self.theme = theme
        self.is_dark_mode = is_dark_mode
        
        # Set category color styles
        self.update_category_color()
        
        # Apply theme to buttons and other elements
        if theme:
            secondary_bg = theme.get("secondary_bg", "#ffffff")
            fg_color = theme.get("fg_color", "#333333")
            danger_color = theme.get("danger_color", "#f44336")
            
            # Style the delete button
            self.delete_btn.setStyleSheet(f"background-color: {danger_color};")
            
            # Style markdown preview
            self.md_preview.setStyleSheet(f"""
                background-color: {secondary_bg};
                color: {fg_color};
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            """)
    
    def update_category_color(self):
        """Update the UI based on the snippet's category/label."""
        # Get the category color
        category = self.label_edit.text()
        category_color = CATEGORY_COLORS.get(category, CATEGORY_COLORS["default"])
        
        # Add template/markdown indicators to the style
        extra_styles = ""
        if self.is_markdown:
            extra_styles += "border-right: 3px solid #2979ff;"  # Blue for markdown
        if self.is_template:
            extra_styles += "border-top: 3px solid #4caf50;"  # Green for template
        
        # Update frame style
        secondary_bg = self.theme.get("secondary_bg", "#ffffff")
        self.setStyleSheet(f"""
            QFrame {{
                border-left: 5px solid {category_color};
                {extra_styles}
                background-color: {secondary_bg};
                border-radius: 4px;
                margin-bottom: 5px;
            }}
        """)
        
        # Update label colors
        self.label_edit.setStyleSheet(f"""
            QLineEdit {{
                font-weight: bold;
                font-size: 13px;
                color: {category_color};
                border: none;
                background-color: transparent;
            }}
        """)
        
        # Update action buttons
        self.expand_btn.setStyleSheet(f"background-color: {category_color};")
        self.mask_btn.setStyleSheet(f"background-color: {category_color};")
    
    def set_row_number(self, number):
        """Update the row number of this snippet."""
        self.row_num = number
        self.row_label.setText(f"{number}.")
    
    def get_text(self):
        """Get the current text content."""
        return self.text_edit.toPlainText()
    
    def get_label(self):
        """Get the current label/category."""
        return self.label_edit.text()
    
    def get_tags(self):
        """Get the current tags."""
        return self.tags
    
    def is_markdown_enabled(self):
        """Check if markdown is enabled."""
        return self.is_markdown
    
    def is_template_enabled(self):
        """Check if this is a template snippet."""
        return self.is_template
    
    def get_snippet_data(self):
        """Get all snippet data as a dictionary."""
        return {
            "text": self.get_text(),
            "label": self.get_label(),
            "tags": self.get_tags(),
            "is_markdown": self.is_markdown_enabled(),
            "is_template": self.is_template_enabled()
        }
    
    def set_tags(self, tags):
        """Set the tags for this snippet."""
        self.tags = tags
        self.refresh_tags_ui()
    
    def refresh_tags_ui(self):
        """Refresh the tags UI."""
        # Clear existing tags
        for i in reversed(range(self.tags_container_layout.count())):
            widget = self.tags_container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add tag labels
        for tag in self.tags:
            tag_label = TagLabel(tag)
            tag_label.remove_clicked.connect(self.remove_tag)
            self.tags_container_layout.addWidget(tag_label)
    
    def add_tag(self, tag):
        """Add a tag to this snippet."""
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.refresh_tags_ui()
            self.content_changed.emit()
            self.tag_added.emit(tag)
    
    def remove_tag(self, tag):
        """Remove a tag from this snippet."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.refresh_tags_ui()
            self.content_changed.emit()
            self.tag_removed.emit(tag)
    
    def show_add_tag_menu(self):
        """Show the add tag context menu."""
        menu = QMenu(self)
        
        # Add a new tag option
        add_new_action = QAction("Add New Tag...", self)
        add_new_action.triggered.connect(self.add_new_tag)
        menu.addAction(add_new_action)
        
        # Add common tags submenu
        common_tags = ["work", "personal", "shopping", "code", "login", "email"]
        if common_tags:
            common_menu = QMenu("Common Tags", menu)
            for tag in common_tags:
                action = QAction(tag, self)
                action.triggered.connect(lambda checked, t=tag: self.add_tag(t))
                common_menu.addAction(action)
            menu.addMenu(common_menu)
        
        # Show menu at button position
        menu.exec(self.add_tag_btn.mapToGlobal(self.add_tag_btn.rect().bottomLeft()))
    
    def add_new_tag(self):
        """Add a new tag via a dialog."""
        from PyQt6.QtWidgets import QInputDialog
        tag, ok = QInputDialog.getText(self, "Add Tag", "Enter tag name:")
        if ok and tag:
            self.add_tag(tag.strip())
    
    def set_markdown_enabled(self, enabled):
        """Enable or disable markdown rendering."""
        self.is_markdown = enabled
        self.markdown_check.setChecked(enabled)
        
        if enabled:
            self.render_markdown()
            self.md_preview.setHidden(False)
        else:
            self.md_preview.setHidden(True)
        
        self.update_category_color()
        self.content_changed.emit()
    
    def toggle_markdown(self, enabled):
        """Toggle markdown rendering."""
        self.set_markdown_enabled(enabled)
    
    def render_markdown(self):
        """Render markdown content to HTML."""
        text = self.text_edit.toPlainText()
        if not text:
            self.md_preview.setText("")
            return
            
        if HAS_MARKDOWN:
            html = markdown.markdown(text)
            self.md_preview.setText(html)
        else:
            self.md_preview.setText("<i>Markdown rendering requires the 'markdown' package. Install with: pip install markdown</i>")
    
    def set_template_enabled(self, enabled):
        """Enable or disable template functionality."""
        self.is_template = enabled
        self.template_check.setChecked(enabled)
        self.use_template_btn.setHidden(not enabled)
        self.update_category_color()
        self.content_changed.emit()
    
    def toggle_template(self, enabled):
        """Toggle template functionality."""
        self.set_template_enabled(enabled)
    
    def use_as_template(self):
        """Use this snippet as a template."""
        self.apply_template.emit(self.get_text())
    
    def on_text_changed(self):
        """Handle text changes."""
        self.text = self.text_edit.toPlainText()
        self.original_text = self.text
        
        if self.is_markdown:
            self.render_markdown()
            
        self.content_changed.emit()
    
    def on_label_changed(self):
        """Handle label changes."""
        self.label = self.label_edit.text()
        self.update_category_color()
        self.content_changed.emit()
    
    def toggle_expansion(self):
        """Toggle between expanded and collapsed states."""
        if self.is_expanded:
            # Collapse
            self.text_edit.setMinimumHeight(70)
            self.text_edit.setMaximumHeight(70)
            self.expand_btn.setText("⬍")  # Down arrow
            self.is_expanded = False
        else:
            # Expand
            self.text_edit.setMinimumHeight(70)
            self.text_edit.setMaximumHeight(200)
            self.expand_btn.setText("⬆")  # Up arrow
            self.is_expanded = True
    
    def toggle_sensitive_data(self):
        """Toggle between masked and unmasked sensitive data."""
        if self.is_masked:
            # Unmask - restore original text
            self.text_edit.blockSignals(True)  # Prevent triggering textChanged
            self.text_edit.setText(self.original_text)
            self.text_edit.blockSignals(False)
            self.mask_btn.setText("👁️")
            self.is_masked = False
        else:
            # Mask - hide sensitive data
            self.original_text = self.text_edit.toPlainText()
            masked_text = mask_sensitive_data(self.original_text)
            self.text_edit.blockSignals(True)  # Prevent triggering textChanged
            self.text_edit.setText(masked_text)
            self.text_edit.blockSignals(False)
            self.mask_btn.setText("👁️‍🗨️")
            self.is_masked = True
    
    def copy_text(self):
        """Copy text and emit signal."""
        text = self.text_edit.toPlainText()
        self.copy_requested.emit(text)
    
    def delete_snippet(self):
        """Delete this snippet."""
        self.delete_requested.emit(self)
    
    def is_selected(self):
        """Check if this snippet is selected."""
        return self.selected
    
    def set_selection_mode(self, enabled):
        """Enable or disable selection mode."""
        self.selection_mode = enabled
        self.select_checkbox.setHidden(not enabled)
        
        if not enabled:
            self.selected = False
            self.select_checkbox.setChecked(False)
    
    def on_selection_toggled(self, checked):
        """Handle selection checkbox toggle."""
        self.selected = checked
        self.selection_changed.emit()
    
    def set_selected(self, selected):
        """Set the selection state programmatically."""
        self.selected = selected
        self.select_checkbox.setChecked(selected)
        
    def set_label(self, label):
        """Set the label/category."""
        self.label = label
        self.label_edit.setText(label)
        self.update_category_color() 