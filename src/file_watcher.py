import os
import time
from pathlib import Path
from typing import Dict, Set, Callable
from threading import Thread, Lock

class FileWatcher:
    def __init__(self, project_root: Path, callback: Callable):
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.callback = callback
        self.file_mtimes: Dict[str, float] = {}
        self.watching = False
        self.watch_thread = None
        self.lock = Lock()
        
    def start(self):
        """Start watching for file changes"""
        if self.watching:
            return
            
        self.watching = True
        self._scan_files()
        self.watch_thread = Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
    
    def stop(self):
        """Stop watching for file changes"""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1)
    
    def _scan_files(self):
        """Scan project for documentation files and record modification times"""
        patterns = ['**/*.adoc', '**/*.md', '**/*.asciidoc']
        
        with self.lock:
            self.file_mtimes.clear()
            for pattern in patterns:
                for file_path in self.project_root.glob(pattern):
                    try:
                        mtime = file_path.stat().st_mtime
                        self.file_mtimes[str(file_path)] = mtime
                    except OSError:
                        pass
    
    def _watch_loop(self):
        """Main watching loop"""
        while self.watching:
            try:
                changed_files = self._check_changes()
                if changed_files:
                    self.callback(changed_files)
                time.sleep(1)  # Check every second
            except Exception:
                pass  # Continue watching even on errors
    
    def _check_changes(self) -> Set[str]:
        """Check for file changes and return set of changed files"""
        changed_files = set()
        current_files = {}
        
        # Scan current files
        patterns = ['**/*.adoc', '**/*.md', '**/*.asciidoc']
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                try:
                    mtime = file_path.stat().st_mtime
                    current_files[str(file_path)] = mtime
                except OSError:
                    continue
        
        with self.lock:
            # Check for new or modified files
            for file_path, mtime in current_files.items():
                if file_path not in self.file_mtimes or self.file_mtimes[file_path] != mtime:
                    changed_files.add(file_path)
            
            # Check for deleted files
            for file_path in self.file_mtimes:
                if file_path not in current_files:
                    changed_files.add(file_path)
            
            # Update stored modification times
            self.file_mtimes = current_files
        
        return changed_files
