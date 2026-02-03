#!/usr/bin/env python3
"""
Desktop Task Management Application
A modern task manager built with tkinter to replace markdown-based todo lists
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
from datetime import datetime, date
import webbrowser
from pathlib import Path
import shutil

class Task:
    def __init__(self, title, description="", priority="Medium", status="Active", 
                 category="General", tags=None, due_date=None, created_date=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.category = category
        self.tags = tags or []
        self.due_date = due_date
        self.created_date = created_date or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.completed_date = None
        self.id = self.generate_id()
    
    def generate_id(self):
        return f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'tags': self.tags,
            'due_date': self.due_date,
            'created_date': self.created_date,
            'completed_date': self.completed_date
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Active'),
            category=data.get('category', 'General'),
            tags=data.get('tags', []),
            due_date=data.get('due_date'),
            created_date=data.get('created_date')
        )
        task.id = data.get('id', task.id)
        task.completed_date = data.get('completed_date')
        return task

class TaskManager:
    def __init__(self, data_file="tasks.json"):
        self.data_file = data_file
        self.tasks = []
        self.backup_dir = "backups"
        self.load_tasks()
    
    def load_tasks(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []
    
    def save_tasks(self):
        try:
            # Create backup before saving
            self.create_backup()
            
            data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def create_backup(self):
        try:
            if os.path.exists(self.data_file):
                os.makedirs(self.backup_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"tasks_backup_{timestamp}.json")
                shutil.copy2(self.data_file, backup_file)
                
                # Keep only last 10 backups
                self.cleanup_old_backups()
        except Exception as e:
            print(f"Error creating backup: {e}")
    
    def cleanup_old_backups(self, max_backups=10):
        try:
            if os.path.exists(self.backup_dir):
                backup_files = sorted([f for f in os.listdir(self.backup_dir) if f.startswith("tasks_backup_")])
                if len(backup_files) > max_backups:
                    for old_backup in backup_files[:-max_backups]:
                        os.remove(os.path.join(self.backup_dir, old_backup))
        except Exception as e:
            print(f"Error cleaning up backups: {e}")
    
    def add_task(self, task):
        self.tasks.append(task)
        return self.save_tasks()
    
    def update_task(self, task_id, **kwargs):
        for task in self.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                if kwargs.get('status') == 'Completed' and not task.completed_date:
                    task.completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
                return self.save_tasks()
        return False
    
    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]
        return self.save_tasks()
    
    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_filtered_tasks(self, status=None, priority=None, category=None, search_text=""):
        filtered = self.tasks
        
        if status and status != "All":
            filtered = [task for task in filtered if task.status == status]
        
        if priority and priority != "All":
            filtered = [task for task in filtered if task.priority == priority]
        
        if category and category != "All":
            filtered = [task for task in filtered if task.category == category]
        
        if search_text:
            search_text = search_text.lower()
            filtered = [task for task in filtered 
                       if search_text in task.title.lower() or 
                          search_text in task.description.lower() or
                          any(search_text in tag.lower() for tag in task.tags)]
        
        return filtered
    
    def get_categories(self):
        categories = set(task.category for task in self.tasks)
        return sorted(list(categories))
    
    def get_statistics(self):
        total = len(self.tasks)
        completed = len([task for task in self.tasks if task.status == "Completed"])
        active = len([task for task in self.tasks if task.status == "Active"])
        blocked = len([task for task in self.tasks if task.status == "Blocked"])
        
        priority_stats = {}
        for priority in ["High", "Medium", "Low"]:
            priority_stats[priority] = len([task for task in self.tasks if task.priority == priority])
        
        return {
            "total": total,
            "completed": completed,
            "active": active,
            "blocked": blocked,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "priorities": priority_stats
        }

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager Pro")
        self.root.geometry("1200x800")
        
        # Initialize task manager
        self.task_manager = TaskManager()
        
        # Theme settings
        self.dark_mode = tk.BooleanVar(value=False)
        self.current_theme = "light"
        
        # Filter variables
        self.filter_status = tk.StringVar(value="All")
        self.filter_priority = tk.StringVar(value="All")
        self.filter_category = tk.StringVar(value="All")
        self.search_var = tk.StringVar()
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        
        # Load initial data
        self.refresh_task_list()
        self.update_statistics()
    
    def setup_styles(self):
        self.style = ttk.Style()
        
        # Configure styles for light and dark themes
        self.light_colors = {
            'bg': '#ffffff',
            'fg': '#000000',
            'secondary_bg': '#f0f0f0',
            'accent': '#007acc',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
        
        self.dark_colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'secondary_bg': '#3c3c3c',
            'accent': '#4a9eff',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336'
        }
        
        self.apply_theme(self.current_theme)
    
    def apply_theme(self, theme):
        colors = self.dark_colors if theme == "dark" else self.light_colors
        
        # Configure ttk styles
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=colors['bg'])
        self.style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        self.style.configure('TButton', background=colors['secondary_bg'], foreground=colors['fg'])
        self.style.configure('TEntry', fieldbackground=colors['secondary_bg'], foreground=colors['fg'])
        self.style.configure('TCombobox', fieldbackground=colors['secondary_bg'], foreground=colors['fg'])
        self.style.configure('Treeview', background=colors['secondary_bg'], foreground=colors['fg'], fieldbackground=colors['secondary_bg'])
        self.style.configure('Treeview.Heading', background=colors['secondary_bg'], foreground=colors['fg'])
        
        # Configure root window
        self.root.configure(bg=colors['bg'])
    
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(self.current_theme)
    
    def setup_ui(self):
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        self.create_toolbar(main_frame)
        
        # Create main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Left panel - Filters and statistics
        left_panel = ttk.Frame(content_frame, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        self.create_filters_panel(left_panel)
        self.create_statistics_panel(left_panel)
        
        # Right panel - Task list and details
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_task_list_panel(right_panel)
        self.create_task_details_panel(right_panel)
        
        # Create status bar
        self.create_status_bar(main_frame)
    
    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # New Task button
        new_btn = ttk.Button(toolbar, text="New Task", command=self.new_task, style='Accent.TButton')
        new_btn.pack(side=tk.LEFT, padx=2)
        
        # Edit Task button
        edit_btn = ttk.Button(toolbar, text="Edit Task", command=self.edit_task)
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete Task button
        delete_btn = ttk.Button(toolbar, text="Delete Task", command=self.delete_task)
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Import/Export buttons
        import_btn = ttk.Button(toolbar, text="Import", command=self.import_tasks)
        import_btn.pack(side=tk.LEFT, padx=2)
        
        export_btn = ttk.Button(toolbar, text="Export", command=self.export_tasks)
        export_btn.pack(side=tk.LEFT, padx=2)
        
        # Theme toggle
        theme_btn = ttk.Button(toolbar, text="🌙" if self.current_theme == "light" else "☀️", 
                              command=self.toggle_theme, width=3)
        theme_btn.pack(side=tk.RIGHT, padx=2)
    
    def create_filters_panel(self, parent):
        filters_frame = ttk.LabelFrame(parent, text="Filters", padding=5)
        filters_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search
        ttk.Label(filters_frame, text="Search:").pack(anchor=tk.W)
        search_entry = ttk.Entry(filters_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=2)
        search_entry.bind('<KeyRelease>', lambda e: self.refresh_task_list())
        
        # Status filter
        ttk.Label(filters_frame, text="Status:").pack(anchor=tk.W, pady=(5, 0))
        status_combo = ttk.Combobox(filters_frame, textvariable=self.filter_status, 
                                   values=["All", "Active", "Completed", "Blocked"],
                                   state="readonly", width=15)
        status_combo.pack(fill=tk.X, pady=2)
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Priority filter
        ttk.Label(filters_frame, text="Priority:").pack(anchor=tk.W, pady=(5, 0))
        priority_combo = ttk.Combobox(filters_frame, textvariable=self.filter_priority,
                                     values=["All", "High", "Medium", "Low"],
                                     state="readonly", width=15)
        priority_combo.pack(fill=tk.X, pady=2)
        priority_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Category filter
        ttk.Label(filters_frame, text="Category:").pack(anchor=tk.W, pady=(5, 0))
        categories = ["All"] + self.task_manager.get_categories()
        category_combo = ttk.Combobox(filters_frame, textvariable=self.filter_category,
                                     values=categories, state="readonly", width=15)
        category_combo.pack(fill=tk.X, pady=2)
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_task_list())
        
        # Clear filters button
        clear_btn = ttk.Button(filters_frame, text="Clear Filters", 
                              command=self.clear_filters)
        clear_btn.pack(pady=5)
    
    def create_statistics_panel(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=5)
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_labels = {}
        stats = ["Total", "Active", "Completed", "Blocked", "Completion Rate"]
        
        for stat in stats:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=1)
            ttk.Label(frame, text=f"{stat}:", width=12).pack(side=tk.LEFT)
            self.stats_labels[stat.lower().replace(" ", "_")] = ttk.Label(frame, text="0")
            self.stats_labels[stat.lower().replace(" ", "_")].pack(side=tk.LEFT)
    
    def create_task_list_panel(self, parent):
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Create treeview with scrollbars
        columns = ("Title", "Priority", "Status", "Category", "Due Date")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=15)
        
        # Define column headings
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Category", text="Category")
        self.task_tree.heading("Due Date", text="Due Date")
        
        # Configure column widths
        self.task_tree.column("#0", width=50)
        self.task_tree.column("Title", width=300)
        self.task_tree.column("Priority", width=80)
        self.task_tree.column("Status", width=80)
        self.task_tree.column("Category", width=100)
        self.task_tree.column("Due Date", width=100)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.task_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        self.task_tree.bind('<Double-1>', lambda e: self.edit_task())
    
    def create_task_details_panel(self, parent):
        details_frame = ttk.LabelFrame(parent, text="Task Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget for details
        self.details_text = tk.Text(details_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Add scrollbar
        details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        # Make text widget read-only
        self.details_text.config(state=tk.DISABLED)
    
    def create_status_bar(self, parent):
        self.status_bar = ttk.Label(parent, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def refresh_task_list(self):
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get filtered tasks
        filtered_tasks = self.task_manager.get_filtered_tasks(
            status=self.filter_status.get(),
            priority=self.filter_priority.get(),
            category=self.filter_category.get(),
            search_text=self.search_var.get()
        )
        
        # Add tasks to tree
        for task in filtered_tasks:
            # Determine priority color
            priority_color = ""
            if task.priority == "High":
                priority_color = "red"
            elif task.priority == "Medium":
                priority_color = "orange"
            elif task.priority == "Low":
                priority_color = "green"
            
            # Insert task
            self.task_tree.insert('', 'end', text=task.id[:8], 
                                values=(task.title, task.priority, task.status, 
                                       task.category, task.due_date or ""))
        
        # Update statistics
        self.update_statistics()
        
        # Update status bar
        self.status_bar.config(text=f"Showing {len(filtered_tasks)} of {len(self.task_manager.tasks)} tasks")
    
    def update_statistics(self):
        stats = self.task_manager.get_statistics()
        
        self.stats_labels['total'].config(text=str(stats['total']))
        self.stats_labels['active'].config(text=str(stats['active']))
        self.stats_labels['completed'].config(text=str(stats['completed']))
        self.stats_labels['blocked'].config(text=str(stats['blocked']))
        self.stats_labels['completion_rate'].config(text=f"{stats['completion_rate']:.1f}%")
    
    def on_task_select(self, event):
        selection = self.task_tree.selection()
        if selection:
            item = self.task_tree.item(selection[0])
            task_id = item['text']
            
            # Find full task ID
            task = None
            for t in self.task_manager.tasks:
                if t.id.startswith(task_id):
                    task = t
                    break
            
            if task:
                self.show_task_details(task)
    
    def show_task_details(self, task):
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        details = f"""Title: {task.title}
Description: {task.description or 'No description'}
Priority: {task.priority}
Status: {task.status}
Category: {task.category}
Tags: {', '.join(task.tags) if task.tags else 'None'}
Due Date: {task.due_date or 'Not set'}
Created: {task.created_date}
Completed: {task.completed_date or 'Not completed'}
"""
        
        self.details_text.insert(1.0, details)
        self.details_text.config(state=tk.DISABLED)
    
    def new_task(self):
        task_dialog = TaskDialog(self.root, "New Task")
        if task_dialog.result:
            task = Task(**task_dialog.result)
            if self.task_manager.add_task(task):
                self.refresh_task_list()
                self.status_bar.config(text="Task created successfully")
            else:
                messagebox.showerror("Error", "Failed to create task")
    
    def edit_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return
        
        item = self.task_tree.item(selection[0])
        task_id = item['text']
        
        # Find full task ID
        task = None
        for t in self.task_manager.tasks:
            if t.id.startswith(task_id):
                task = t
                break
        
        if task:
            task_dialog = TaskDialog(self.root, "Edit Task", task)
            if task_dialog.result:
                if self.task_manager.update_task(task.id, **task_dialog.result):
                    self.refresh_task_list()
                    self.status_bar.config(text="Task updated successfully")
                else:
                    messagebox.showerror("Error", "Failed to update task")
    
    def delete_task(self):
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            item = self.task_tree.item(selection[0])
            task_id = item['text']
            
            # Find full task ID
            task = None
            for t in self.task_manager.tasks:
                if t.id.startswith(task_id):
                    task = t
                    break
            
            if task and self.task_manager.delete_task(task.id):
                self.refresh_task_list()
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.config(state=tk.DISABLED)
                self.status_bar.config(text="Task deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete task")
    
    def clear_filters(self):
        self.filter_status.set("All")
        self.filter_priority.set("All")
        self.filter_category.set("All")
        self.search_var.set("")
        self.refresh_task_list()
    
    def import_tasks(self):
        filename = filedialog.askopenfilename(
            title="Import Tasks",
            filetypes=[("JSON files", "*.json"), ("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.md'):
                    self.import_markdown_tasks(filename)
                else:
                    self.import_json_tasks(filename)
                self.refresh_task_list()
                self.status_bar.config(text="Tasks imported successfully")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import tasks: {str(e)}")
    
    def import_markdown_tasks(self, filename):
        """Import tasks from markdown format"""
        with open(filename, 'r') as f:
            content = f.read()
        
        # Simple markdown parsing - looks for lines starting with - [ ] or - [x]
        tasks = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- [ ]'):
                title = line[5:].strip()
                if title:
                    task = Task(title=title, status="Active")
                    tasks.append(task)
            elif line.startswith('- [x]'):
                title = line[5:].strip()
                if title:
                    task = Task(title=title, status="Completed")
                    tasks.append(task)
        
        # Add imported tasks
        for task in tasks:
            self.task_manager.add_task(task)
        
        messagebox.showinfo("Import Complete", f"Imported {len(tasks)} tasks from markdown")
    
    def import_json_tasks(self, filename):
        """Import tasks from JSON format"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        tasks = [Task.from_dict(task_data) for task_data in data]
        
        # Add imported tasks
        for task in tasks:
            self.task_manager.add_task(task)
        
        messagebox.showinfo("Import Complete", f"Imported {len(tasks)} tasks from JSON")
    
    def export_tasks(self):
        filename = filedialog.asksaveasfilename(
            title="Export Tasks",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.csv'):
                    self.export_csv_tasks(filename)
                else:
                    self.export_json_tasks(filename)
                self.status_bar.config(text="Tasks exported successfully")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")
    
    def export_json_tasks(self, filename):
        """Export tasks to JSON format"""
        data = [task.to_dict() for task in self.task_manager.tasks]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        messagebox.showinfo("Export Complete", f"Exported {len(data)} tasks to JSON")
    
    def export_csv_tasks(self, filename):
        """Export tasks to CSV format"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Title', 'Description', 'Priority', 'Status', 'Category', 
                           'Tags', 'Due Date', 'Created Date', 'Completed Date'])
            
            for task in self.task_manager.tasks:
                writer.writerow([
                    task.title,
                    task.description,
                    task.priority,
                    task.status,
                    task.category,
                    ', '.join(task.tags),
                    task.due_date or '',
                    task.created_date,
                    task.completed_date or ''
                ])
        
        messagebox.showinfo("Export Complete", f"Exported {len(self.task_manager.tasks)} tasks to CSV")

class TaskDialog(tk.Toplevel):
    def __init__(self, parent, title, task=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.result = None
        self.task = task
        
        # Create form fields
        self.create_form()
        
        # Load task data if editing
        if task:
            self.load_task_data()
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def create_form(self):
        # Title
        ttk.Label(self, text="Title:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(self, textvariable=self.title_var, width=50)
        title_entry.pack(fill=tk.X, padx=10)
        title_entry.focus()
        
        # Description
        ttk.Label(self, text="Description:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.description_text = tk.Text(self, height=6, width=50)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Priority
        ttk.Label(self, text="Priority:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(self, textvariable=self.priority_var,
                                     values=["High", "Medium", "Low"], state="readonly")
        priority_combo.pack(fill=tk.X, padx=10)
        
        # Status
        ttk.Label(self, text="Status:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.status_var = tk.StringVar(value="Active")
        status_combo = ttk.Combobox(self, textvariable=self.status_var,
                                   values=["Active", "Completed", "Blocked"], state="readonly")
        status_combo.pack(fill=tk.X, padx=10)
        
        # Category
        ttk.Label(self, text="Category:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.category_var = tk.StringVar(value="General")
        category_combo = ttk.Combobox(self, textvariable=self.category_var,
                                     values=["General", "Work", "Personal", "Shopping", "Health", "Education"])
        category_combo.pack(fill=tk.X, padx=10)
        
        # Tags
        ttk.Label(self, text="Tags (comma-separated):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.tags_var = tk.StringVar()
        tags_entry = ttk.Entry(self, textvariable=self.tags_var, width=50)
        tags_entry.pack(fill=tk.X, padx=10)
        
        # Due Date
        ttk.Label(self, text="Due Date (YYYY-MM-DD):").pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.due_date_var = tk.StringVar()
        due_date_entry = ttk.Entry(self, textvariable=self.due_date_var, width=50)
        due_date_entry.pack(fill=tk.X, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        save_btn = ttk.Button(button_frame, text="Save", command=self.save_task)
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter key to save
        self.bind('<Return>', lambda e: self.save_task())
    
    def load_task_data(self):
        self.title_var.set(self.task.title)
        self.description_text.insert(1.0, self.task.description)
        self.priority_var.set(self.task.priority)
        self.status_var.set(self.task.status)
        self.category_var.set(self.task.category)
        self.tags_var.set(', '.join(self.task.tags))
        self.due_date_var.set(self.task.due_date or "")
    
    def save_task(self):
        # Validate title
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title is required")
            return
        
        # Validate due date format if provided
        due_date = self.due_date_var.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
        
        # Prepare result
        self.result = {
            'title': title,
            'description': self.description_text.get(1.0, tk.END).strip(),
            'priority': self.priority_var.get(),
            'status': self.status_var.get(),
            'category': self.category_var.get(),
            'tags': [tag.strip() for tag in self.tags_var.get().split(',') if tag.strip()],
            'due_date': due_date if due_date else None
        }
        
        self.destroy()

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()