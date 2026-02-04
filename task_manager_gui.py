#!/usr/bin/env python3
"""
Task Manager GUI Application
A comprehensive task management tool with modern interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from datetime import datetime, date
import os
from pathlib import Path

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager Pro")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Data storage
        self.tasks = []
        self.current_filter = "All"
        self.search_term = ""
        
        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_main_layout()
        self.create_task_form()
        self.create_task_list()
        
        # Load existing tasks
        self.load_tasks()
        
    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'bg': '#f8f9fa',
            'fg': '#2c3e50',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'high': '#e74c3c',
            'medium': '#f39c12',
            'low': '#27ae60'
        }
        
        # Configure styles
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['accent'], foreground='white')
        style.map('TButton', background=[('active', '#2980b9')])
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Task", command=self.clear_form)
        file_menu.add_separator()
        file_menu.add_command(label="Import Tasks", command=self.import_tasks)
        file_menu.add_command(label="Export Tasks", command=self.export_tasks)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_task_list)
        
    def create_main_layout(self):
        """Create main application layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Task form
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel - Task list
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.left_frame = left_frame
        self.right_frame = right_frame
        
    def create_task_form(self):
        """Create task input form"""
        form_frame = ttk.LabelFrame(self.left_frame, text="Task Details", padding=10)
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Task Title
        ttk.Label(form_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(form_frame, textvariable=self.title_var, width=30)
        title_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.desc_text = tk.Text(form_frame, height=4, width=30, wrap=tk.WORD)
        self.desc_text.grid(row=1, column=1, sticky=tk.EW, pady=2)
        
        # Category
        ttk.Label(form_frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                     values=["Personal", "Work", "Shopping", "Health", "Other"])
        category_combo.grid(row=2, column=1, sticky=tk.EW, pady=2)
        category_combo.set("Personal")
        
        # Priority
        ttk.Label(form_frame, text="Priority:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = ttk.Frame(form_frame)
        priority_frame.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Radiobutton(priority_frame, text="High", variable=self.priority_var, 
                       value="High").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Medium", variable=self.priority_var, 
                       value="Medium").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Low", variable=self.priority_var, 
                       value="Low").pack(side=tk.LEFT)
        
        # Due Date
        ttk.Label(form_frame, text="Due Date:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.due_date_var = tk.StringVar()
        due_date_entry = ttk.Entry(form_frame, textvariable=self.due_date_var, width=20)
        due_date_entry.grid(row=4, column=1, sticky=tk.W, pady=2)
        due_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Progress
        ttk.Label(form_frame, text="Progress:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.progress_var = tk.IntVar(value=0)
        progress_scale = ttk.Scale(form_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                  variable=self.progress_var, command=self.update_progress_label)
        progress_scale.grid(row=5, column=1, sticky=tk.EW, pady=2)
        
        self.progress_label = ttk.Label(form_frame, text="0%")
        self.progress_label.grid(row=5, column=2, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Update Task", command=self.update_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
    def create_task_list(self):
        """Create task list display"""
        # Filter frame
        filter_frame = ttk.Frame(self.right_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.filter_tasks)
        
        # Status filter
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_filter_var,
                                   values=["All", "To Do", "In Progress", "Done"], width=12)
        status_combo.pack(side=tk.LEFT, padx=(0, 10))
        status_combo.bind('<<ComboboxSelected>>', self.filter_tasks)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter_var,
                                     values=["All", "Personal", "Work", "Shopping", "Health", "Other"], width=12)
        category_combo.pack(side=tk.LEFT, padx=(0, 10))
        category_combo.bind('<<ComboboxSelected>>', self.filter_tasks)
        
        # Refresh button
        ttk.Button(filter_frame, text="Refresh", command=self.refresh_task_list).pack(side=tk.RIGHT)
        
        # Task list frame
        list_frame = ttk.Frame(self.right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview with scrollbars
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.task_tree = ttk.Treeview(tree_frame, columns=('ID', 'Title', 'Category', 'Priority', 'Status', 'Due Date', 'Progress'),
                                     yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set,
                                     selectmode='browse')
        
        # Configure columns
        self.task_tree.heading('#0', text='')
        self.task_tree.heading('ID', text='ID')
        self.task_tree.heading('Title', text='Title')
        self.task_tree.heading('Category', text='Category')
        self.task_tree.heading('Priority', text='Priority')
        self.task_tree.heading('Status', text='Status')
        self.task_tree.heading('Due Date', text='Due Date')
        self.task_tree.heading('Progress', text='Progress')
        
        # Configure column widths
        self.task_tree.column('#0', width=0, stretch=tk.NO)
        self.task_tree.column('ID', width=50, stretch=tk.NO)
        self.task_tree.column('Title', width=200)
        self.task_tree.column('Category', width=100)
        self.task_tree.column('Priority', width=80, stretch=tk.NO)
        self.task_tree.column('Status', width=100, stretch=tk.NO)
        self.task_tree.column('Due Date', width=100, stretch=tk.NO)
        self.task_tree.column('Progress', width=100, stretch=tk.NO)
        
        # Pack treeview
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.task_tree.yview)
        h_scrollbar.config(command=self.task_tree.xview)
        
        # Bind events
        self.task_tree.bind('<<TreeviewSelect>>', self.on_task_select)
        self.task_tree.bind('<Double-1>', self.on_task_double_click)
        
        # Context menu
        self.create_context_menu()
        
    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Task", command=self.edit_selected_task)
        self.context_menu.add_command(label="Delete Task", command=self.delete_selected_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Mark as To Do", command=lambda: self.update_task_status("To Do"))
        self.context_menu.add_command(label="Mark as In Progress", command=lambda: self.update_task_status("In Progress"))
        self.context_menu.add_command(label="Mark as Done", command=lambda: self.update_task_status("Done"))
        
        self.task_tree.bind('<Button-3>', self.show_context_menu)
        
    def show_context_menu(self, event):
        """Show context menu"""
        item = self.task_tree.identify_row(event.y)
        if item:
            self.task_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
            
    def update_progress_label(self, value):
        """Update progress percentage label"""
        self.progress_label.config(text=f"{int(float(value))}%")
        
    def add_task(self):
        """Add new task"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Task title is required!")
            return
            
        task = {
            'id': len(self.tasks) + 1,
            'title': title,
            'description': self.desc_text.get('1.0', tk.END).strip(),
            'category': self.category_var.get(),
            'priority': self.priority_var.get(),
            'status': 'To Do',
            'due_date': self.due_date_var.get(),
            'progress': self.progress_var.get(),
            'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.tasks.append(task)
        self.clear_form()
        self.refresh_task_list()
        self.save_tasks()
        messagebox.showinfo("Success", "Task added successfully!")
        
    def update_task(self):
        """Update existing task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to update!")
            return
            
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Task title is required!")
            return
            
        # Get selected task ID
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        
        # Find and update task
        for task in self.tasks:
            if task['id'] == task_id:
                task['title'] = title
                task['description'] = self.desc_text.get('1.0', tk.END).strip()
                task['category'] = self.category_var.get()
                task['priority'] = self.priority_var.get()
                task['due_date'] = self.due_date_var.get()
                task['progress'] = self.progress_var.get()
                break
                
        self.clear_form()
        self.refresh_task_list()
        self.save_tasks()
        messagebox.showinfo("Success", "Task updated successfully!")
        
    def delete_selected_task(self):
        """Delete selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete!")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            item = self.task_tree.item(selected[0])
            task_id = int(item['values'][0])
            
            # Remove task
            self.tasks = [task for task in self.tasks if task['id'] != task_id]
            
            # Renumber remaining tasks
            for i, task in enumerate(self.tasks):
                task['id'] = i + 1
                
            self.refresh_task_list()
            self.save_tasks()
            messagebox.showinfo("Success", "Task deleted successfully!")
            
    def edit_selected_task(self):
        """Edit selected task"""
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to edit!")
            return
            
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        
        # Find task
        for task in self.tasks:
            if task['id'] == task_id:
                # Load task data into form
                self.title_var.set(task['title'])
                self.desc_text.delete('1.0', tk.END)
                self.desc_text.insert('1.0', task['description'])
                self.category_var.set(task['category'])
                self.priority_var.set(task['priority'])
                self.due_date_var.set(task['due_date'])
                self.progress_var.set(task['progress'])
                self.update_progress_label(task['progress'])
                break
                
    def update_task_status(self, status):
        """Update status of selected task"""
        selected = self.task_tree.selection()
        if not selected:
            return
            
        item = self.task_tree.item(selected[0])
        task_id = int(item['values'][0])
        
        # Find and update task
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = status
                break
                
        self.refresh_task_list()
        self.save_tasks()
        
    def on_task_select(self, event):
        """Handle task selection"""
        selected = self.task_tree.selection()
        if selected:
            self.edit_selected_task()
            
    def on_task_double_click(self, event):
        """Handle double click on task"""
        selected = self.task_tree.selection()
        if selected:
            # Toggle status
            item = self.task_tree.item(selected[0])
            current_status = item['values'][4]
            
            if current_status == "To Do":
                new_status = "In Progress"
            elif current_status == "In Progress":
                new_status = "Done"
            else:
                new_status = "To Do"
                
            self.update_task_status(new_status)
            
    def filter_tasks(self, event=None):
        """Filter tasks based on search and filters"""
        self.refresh_task_list()
        
    def refresh_task_list(self):
        """Refresh task list display"""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        # Filter tasks
        filtered_tasks = self.tasks.copy()
        
        # Apply search filter
        if self.search_term:
            filtered_tasks = [task for task in filtered_tasks 
                            if self.search_term.lower() in task['title'].lower() or 
                               self.search_term.lower() in task['description'].lower()]
                               
        # Apply status filter
        if self.status_filter_var.get() != "All":
            filtered_tasks = [task for task in filtered_tasks 
                            if task['status'] == self.status_filter_var.get()]
                            
        # Apply category filter
        if self.category_filter_var.get() != "All":
            filtered_tasks = [task for task in filtered_tasks 
                            if task['category'] == self.category_filter_var.get()]
                            
        # Sort by priority and due date
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        filtered_tasks.sort(key=lambda x: (priority_order[x['priority']], x['due_date']))
        
        # Add tasks to tree
        for task in filtered_tasks:
            # Determine row color based on priority
            tags = (task['priority'].lower(),)
            
            self.task_tree.insert('', 'end', values=(
                task['id'],
                task['title'],
                task['category'],
                task['priority'],
                task['status'],
                task['due_date'],
                f"{task['progress']}%"
            ), tags=tags)
            
        # Configure tag colors
        self.task_tree.tag_configure('high', background='#ffe6e6')
        self.task_tree.tag_configure('medium', background='#fff3e6')
        self.task_tree.tag_configure('low', background='#e6ffe6')
        
    def clear_form(self):
        """Clear task form"""
        self.title_var.set("")
        self.desc_text.delete('1.0', tk.END)
        self.category_var.set("Personal")
        self.priority_var.set("Medium")
        self.due_date_var.set(date.today().strftime("%Y-%m-%d"))
        self.progress_var.set(0)
        self.update_progress_label(0)
        
    def save_tasks(self):
        """Save tasks to JSON file"""
        try:
            with open('tasks.json', 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")
            
    def load_tasks(self):
        """Load tasks from JSON file"""
        try:
            if os.path.exists('tasks.json'):
                with open('tasks.json', 'r') as f:
                    self.tasks = json.load(f)
                self.refresh_task_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            
    def export_tasks(self):
        """Export tasks to file"""
        file_types = [
            ("JSON files", "*.json"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=file_types,
            title="Export Tasks"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.tasks, f, indent=2)
                elif filename.endswith('.csv'):
                    with open(filename, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['ID', 'Title', 'Description', 'Category', 'Priority', 
                                       'Status', 'Due Date', 'Progress', 'Created Date'])
                        for task in self.tasks:
                            writer.writerow([
                                task['id'], task['title'], task['description'], 
                                task['category'], task['priority'], task['status'],
                                task['due_date'], task['progress'], task['created_date']
                            ])
                messagebox.showinfo("Success", f"Tasks exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
                
    def import_tasks(self):
        """Import tasks from file"""
        file_types = [
            ("JSON files", "*.json"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            filetypes=file_types,
            title="Import Tasks"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'r') as f:
                        imported_tasks = json.load(f)
                elif filename.endswith('.csv'):
                    imported_tasks = []
                    with open(filename, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            task = {
                                'id': int(row['ID']),
                                'title': row['Title'],
                                'description': row['Description'],
                                'category': row['Category'],
                                'priority': row['Priority'],
                                'status': row['Status'],
                                'due_date': row['Due Date'],
                                'progress': int(row['Progress']),
                                'created_date': row['Created Date']
                            }
                            imported_tasks.append(task)
                            
                # Merge with existing tasks
                if messagebox.askyesno("Confirm", "Import tasks? This will add to existing tasks."):
                    max_id = max([task['id'] for task in self.tasks]) if self.tasks else 0
                    for task in imported_tasks:
                        task['id'] = max_id + 1
                        max_id += 1
                        self.tasks.append(task)
                    
                    self.refresh_task_list()
                    self.save_tasks()
                    messagebox.showinfo("Success", f"Imported {len(imported_tasks)} tasks")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")

def main():
    """Main function"""
    root = tk.Tk()
    app = TaskManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()