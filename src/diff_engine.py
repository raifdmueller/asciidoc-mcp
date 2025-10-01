#!/usr/bin/env python3

import difflib
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DiffLine:
    line_type: str  # 'added', 'removed', 'unchanged'
    content: str
    line_number: int

class DiffEngine:
    """Simple diff engine for content changes"""
    
    def __init__(self):
        self.previous_content = {}
    
    def compare_content(self, section_id: str, old_content: str, new_content: str) -> Dict[str, Any]:
        """Compare two versions of content and return diff"""
        
        old_lines = old_content.splitlines() if old_content else []
        new_lines = new_content.splitlines() if new_content else []
        
        diff_lines = []
        
        # Use difflib for line-by-line comparison
        differ = difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile='old', 
            tofile='new', 
            lineterm=''
        )
        
        changes = {
            'added_lines': 0,
            'removed_lines': 0,
            'changed_lines': 0
        }
        
        line_num = 0
        for line in differ:
            line_num += 1
            if line.startswith('+') and not line.startswith('+++'):
                diff_lines.append(DiffLine('added', line[1:], line_num))
                changes['added_lines'] += 1
            elif line.startswith('-') and not line.startswith('---'):
                diff_lines.append(DiffLine('removed', line[1:], line_num))
                changes['removed_lines'] += 1
            elif not line.startswith('@@') and not line.startswith('+++') and not line.startswith('---'):
                diff_lines.append(DiffLine('unchanged', line[1:] if line.startswith(' ') else line, line_num))
        
        # Calculate change percentage
        total_lines = max(len(old_lines), len(new_lines))
        change_percentage = ((changes['added_lines'] + changes['removed_lines']) / total_lines * 100) if total_lines > 0 else 0
        
        return {
            'section_id': section_id,
            'changes': changes,
            'change_percentage': round(change_percentage, 2),
            'diff_lines': [{'type': d.line_type, 'content': d.content, 'line_number': d.line_number} for d in diff_lines],
            'has_changes': changes['added_lines'] > 0 or changes['removed_lines'] > 0
        }
    
    def track_change(self, section_id: str, content: str) -> Dict[str, Any]:
        """Track a change and return diff from previous version"""
        old_content = self.previous_content.get(section_id, '')
        diff_result = self.compare_content(section_id, old_content, content)
        
        # Store new content for next comparison
        self.previous_content[section_id] = content
        
        return diff_result
    
    def get_html_diff(self, section_id: str, old_content: str, new_content: str) -> str:
        """Generate HTML diff visualization"""
        diff_result = self.compare_content(section_id, old_content, new_content)
        
        html_lines = []
        html_lines.append('<div class="diff-container">')
        html_lines.append(f'<h4>Changes in {section_id}</h4>')
        html_lines.append(f'<p>Added: {diff_result["changes"]["added_lines"]} lines, '
                         f'Removed: {diff_result["changes"]["removed_lines"]} lines, '
                         f'Change: {diff_result["change_percentage"]}%</p>')
        
        for diff_line in diff_result['diff_lines']:
            css_class = {
                'added': 'diff-added',
                'removed': 'diff-removed', 
                'unchanged': 'diff-unchanged'
            }.get(diff_line['type'], '')
            
            html_lines.append(f'<div class="{css_class}">{diff_line["content"]}</div>')
        
        html_lines.append('</div>')
        return '\n'.join(html_lines)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked changes"""
        return {
            'tracked_sections': len(self.previous_content),
            'sections': list(self.previous_content.keys())
        }
