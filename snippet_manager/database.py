"""
Database operations for Snippet Manager Pro.
Handles loading, saving, importing, and exporting snippets.
"""

import os
import json
from datetime import datetime
from .config import SAVE_FILE

class SnippetDatabase:
    """Manages snippet data persistence."""
    
    def __init__(self, save_file=SAVE_FILE):
        """Initialize with the specified save file path."""
        self.save_file = save_file
        
    def save_snippets(self, snippets_data):
        """Save snippets to the JSON file."""
        try:
            # Convert to new schema if needed
            updated_data = []
            for snippet in snippets_data:
                # Ensure each snippet has the new fields if not present
                if not isinstance(snippet.get("tags"), list):
                    snippet["tags"] = []
                    
                if "is_markdown" not in snippet:
                    snippet["is_markdown"] = False
                    
                if "is_template" not in snippet:
                    snippet["is_template"] = False
                    
                updated_data.append(snippet)
                
            with open(self.save_file, "w") as f:
                json.dump(updated_data, f)
            return True, f"Saved {len(updated_data)} snippets"
        except Exception as e:
            return False, f"Error saving: {str(e)}"
    
    def load_snippets(self):
        """Load snippets from the JSON file."""
        # Return default snippets if file doesn't exist
        if not os.path.exists(self.save_file):
            return self._get_default_snippets(), "Created default snippets"
            
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r") as f:
                    saved_snippets = json.load(f)
                
                if isinstance(saved_snippets, list):
                    # Ensure all snippets have the required fields in our schema
                    updated_snippets = []
                    
                    if saved_snippets:
                        for snippet in saved_snippets:
                            if isinstance(snippet, dict):
                                # Add missing fields for older snippets
                                if "text" not in snippet:
                                    snippet["text"] = ""
                                if "label" not in snippet:
                                    snippet["label"] = ""
                                if "tags" not in snippet:
                                    snippet["tags"] = []
                                if "is_markdown" not in snippet:
                                    snippet["is_markdown"] = False
                                if "is_template" not in snippet:
                                    snippet["is_template"] = False
                                
                                updated_snippets.append(snippet)
                            elif isinstance(snippet, str):
                                # Convert old string-only format
                                updated_snippets.append({
                                    "text": snippet,
                                    "label": "",
                                    "tags": [],
                                    "is_markdown": False,
                                    "is_template": False
                                })
                                
                        return updated_snippets, f"Loaded {len(updated_snippets)} saved snippets"
                    return [], "No snippets found"
                return [], "Invalid snippet format"
            except json.JSONDecodeError:
                return [], "Error reading saved snippets file"
            except Exception as e:
                return [], f"Error loading snippets: {str(e)}"
        return [], "No snippets file found"
    
    def _get_default_snippets(self):
        """Create default snippets for first run."""
        # WordPress site credentials
        wp_creds = """Site name: Picayune Fire
        URL: https://picayunefire.s1-tastewp.com
        Username: admin
        Password: sFmKkoOPW_g"""
        
        # Markdown template example
        markdown_template = """# Meeting Notes Template

        ## Meeting Information
        - **Date**: [Date]
        - **Time**: [Time]
        - **Location**: [Location]
        - **Attendees**: [Names]

        ## Agenda
        1. [Topic 1]
        2. [Topic 2]
        3. [Topic 3]

        ## Discussion Points
        * 

        ## Action Items
        - [ ] [Task 1] - Assigned to: [Name]
        - [ ] [Task 2] - Assigned to: [Name]
        - [ ] [Task 3] - Assigned to: [Name]

        ## Next Meeting
        - **Date**: [Date]
        - **Time**: [Time]
        - **Location**: [Location]"""
        
        # Create organized snippets with appropriate labels and tags
        default_snippets = [
            {
                "text": wp_creds, 
                "label": "WordPress Login", 
                "tags": ["credentials", "web"],
                "is_markdown": False,
                "is_template": False
            },
            {
                "text": markdown_template,
                "label": "Meeting Notes",
                "tags": ["template", "business"],
                "is_markdown": True,
                "is_template": True
            }
        ]
        
        return default_snippets
    
    def import_from_file(self, file_path):
        """Import snippets from a file."""
        try:
            # Determine file type from extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == ".json":
                # Import from JSON
                with open(file_path, "r") as f:
                    imported_data = json.load(f)
                
                # Process imported data
                if isinstance(imported_data, list):
                    # Standardize format for all snippets
                    standardized_snippets = []
                    
                    for item in imported_data:
                        if isinstance(item, dict):
                            snippet = {
                                "text": item.get("text", ""),
                                "label": item.get("label", ""),
                                "tags": item.get("tags", []),
                                "is_markdown": item.get("is_markdown", False),
                                "is_template": item.get("is_template", False)
                            }
                            standardized_snippets.append(snippet)
                        elif isinstance(item, str):
                            # Handle string-only items
                            standardized_snippets.append({
                                "text": item,
                                "label": "",
                                "tags": [],
                                "is_markdown": False,
                                "is_template": False
                            })
                    
                    return standardized_snippets, f"Imported {len(standardized_snippets)} snippets from JSON"
            else:
                # Import from text file (one snippet per line)
                with open(file_path, "r") as f:
                    lines = f.readlines()
                
                # Add imported snippets
                imported_data = []
                for line in lines:
                    if line.strip():
                        imported_data.append({
                            "text": line.strip(),
                            "label": "",
                            "tags": [],
                            "is_markdown": False,
                            "is_template": False
                        })
                
                return imported_data, f"Imported {len(imported_data)} snippets from text file"
        except Exception as e:
            return [], f"Import error: {str(e)}"
            
    def export_to_file(self, snippets, file_path, format_type="txt"):
        """Export snippets to a file in the specified format."""
        try:
            with open(file_path, "w") as f:
                if format_type == "txt":
                    # Plain text export
                    for snippet in snippets:
                        label = snippet.get("label", "")
                        text = snippet.get("text", "")
                        tags = snippet.get("tags", [])
                        
                        if label:
                            f.write(f"[{label}]\n")
                        
                        if tags:
                            f.write(f"Tags: {', '.join(tags)}\n")
                            
                        if snippet.get("is_template", False):
                            f.write("[TEMPLATE]\n")
                            
                        if snippet.get("is_markdown", False):
                            f.write("[MARKDOWN]\n")
                            
                        f.write(f"{text}\n\n")
                
                elif format_type == "html":
                    # HTML export with support for Markdown rendering
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                    f.write("<title>Exported Snippets</title>\n")
                    # Add markdown support
                    f.write('<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>\n')
                    f.write("<style>\n")
                    f.write("body { font-family: Arial, sans-serif; margin: 20px; }\n")
                    f.write(".snippet { border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; border-radius: 5px; }\n")
                    f.write(".label { font-weight: bold; color: #333; margin-bottom: 5px; }\n")
                    f.write(".tags { color: #0066cc; font-style: italic; margin-bottom: 5px; }\n")
                    f.write(".badge { display: inline-block; background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; margin-right: 5px; font-size: 0.8em; }\n")
                    f.write(".text { white-space: pre-wrap; }\n")
                    f.write(".markdown { border-left: 3px solid #2979ff; padding-left: 10px; }\n")
                    f.write(".template { border-left: 3px solid #4caf50; padding-left: 10px; }\n")
                    f.write("</style>\n</head>\n<body>\n")
                    f.write(f"<h1>Exported Snippets</h1>\n")
                    f.write(f"<p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n")
                    
                    for i, snippet in enumerate(snippets, 1):
                        label = snippet.get("label", "")
                        text = snippet.get("text", "")
                        tags = snippet.get("tags", [])
                        is_markdown = snippet.get("is_markdown", False)
                        is_template = snippet.get("is_template", False)
                        
                        classes = []
                        if is_markdown:
                            classes.append("markdown")
                        if is_template:
                            classes.append("template")
                            
                        class_attr = f' class="snippet {" ".join(classes)}"' if classes else ' class="snippet"'
                        
                        f.write(f'<div{class_attr}>\n')
                        f.write(f'<div class="label">#{i}: {label}</div>\n')
                        
                        if tags:
                            f.write('<div class="tags">Tags: ')
                            for tag in tags:
                                f.write(f'<span class="badge">{tag}</span>')
                            f.write('</div>\n')
                        
                        if is_markdown:
                            f.write(f'<div class="text markdown-content" data-markdown="{text.replace('"', '&quot;')}"></div>\n')
                        else:
                            f.write(f'<div class="text">{text}</div>\n')
                        
                        f.write(f'</div>\n')
                    
                    # Add script to render Markdown content
                    f.write("""
<script>
  document.addEventListener('DOMContentLoaded', function() {
    var mdContents = document.querySelectorAll('.markdown-content');
    mdContents.forEach(function(element) {
      var markdown = element.getAttribute('data-markdown');
      element.innerHTML = marked.parse(markdown);
    });
  });
</script>
""")
                    f.write("</body>\n</html>")
                
                elif format_type == "md":
                    # Markdown export
                    f.write(f"# Exported Snippets\n\n")
                    f.write(f"Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for i, snippet in enumerate(snippets, 1):
                        label = snippet.get("label", "")
                        text = snippet.get("text", "")
                        tags = snippet.get("tags", [])
                        is_markdown = snippet.get("is_markdown", False)
                        is_template = snippet.get("is_template", False)
                        
                        f.write(f"## {i}. {label}\n\n")
                        
                        if tags:
                            f.write(f"**Tags**: {', '.join(tags)}\n\n")
                            
                        if is_template:
                            f.write("**Template**\n\n")
                            
                        if is_markdown:
                            f.write("**Markdown Content**\n\n")
                            # For markdown content, we can include it directly
                            f.write(f"{text}\n\n")
                        else:
                            # For plain text, wrap in code block
                            f.write(f"```\n{text}\n```\n\n")
            
            return True, f"Exported {len(snippets)} snippets to {format_type.upper()} file"
        
        except Exception as e:
            return False, f"Export error: {str(e)}"
            
    def bulk_update_snippets(self, snippet_ids, update_data):
        """Update multiple snippets at once with the given data.
        
        Args:
            snippet_ids: List of snippet indices to update
            update_data: Dictionary with fields to update
            
        Returns:
            (success, message) tuple
        """
        try:
            # Load all snippets
            snippets, _ = self.load_snippets()
            if not snippets:
                return False, "No snippets to update"
                
            # Update the specified snippets
            updated_count = 0
            for idx in snippet_ids:
                if 0 <= idx < len(snippets):
                    for key, value in update_data.items():
                        snippets[idx][key] = value
                    updated_count += 1
            
            # Save the changes
            if updated_count > 0:
                success, _ = self.save_snippets(snippets)
                if success:
                    return True, f"Updated {updated_count} snippets"
                else:
                    return False, "Failed to save updates"
            else:
                return False, "No snippets were updated"
                
        except Exception as e:
            return False, f"Bulk update error: {str(e)}"
            
    def bulk_delete_snippets(self, snippet_ids):
        """Delete multiple snippets at once.
        
        Args:
            snippet_ids: List of snippet indices to delete
            
        Returns:
            (success, message) tuple
        """
        try:
            # Load all snippets
            snippets, _ = self.load_snippets()
            if not snippets:
                return False, "No snippets to delete"
                
            # Convert to set for O(1) lookup and sort in reverse to avoid index shifting
            indices_to_delete = sorted(set(snippet_ids), reverse=True)
            
            # Delete the specified snippets
            deleted_count = 0
            for idx in indices_to_delete:
                if 0 <= idx < len(snippets):
                    snippets.pop(idx)
                    deleted_count += 1
            
            # Save the changes
            if deleted_count > 0:
                success, _ = self.save_snippets(snippets)
                if success:
                    return True, f"Deleted {deleted_count} snippets"
                else:
                    return False, "Failed to save after deletion"
            else:
                return False, "No snippets were deleted"
                
        except Exception as e:
            return False, f"Bulk delete error: {str(e)}"
            
    def get_all_tags(self):
        """Get a list of all unique tags used in snippets.
        
        Returns:
            List of unique tag strings
        """
        snippets, _ = self.load_snippets()
        
        # Collect all tags
        all_tags = set()
        for snippet in snippets:
            tags = snippet.get("tags", [])
            if tags:
                all_tags.update(tags)
                
        return sorted(list(all_tags))
        
    def get_template_snippets(self):
        """Get all snippets marked as templates.
        
        Returns:
            List of template snippets
        """
        snippets, _ = self.load_snippets()
        
        templates = [s for s in snippets if s.get("is_template", False)]
        return templates 