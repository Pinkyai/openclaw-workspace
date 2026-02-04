#!/usr/bin/env python3
"""
Modern Task Manager - Beautiful GUI
Clean, modern, minimalistic design
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ModernTask:
    def __init__(self, title, description="", priority="Medium", status="Active", due_date=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.completed_date = None
        self.id = self.generate_id()
    
    def generate_id(self):
        import uuid
        return str(uuid.uuid4())[:8]

class ModernTaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Modern Task Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')  # Modern dark background
        
        # Modern color scheme
        self.colors = {
            'bg': '#1a1a1a',           # Dark background
            'fg': '#ffffff',           # White text
            'accent': '#00ff88',       # Green accent
            'secondary': '#888888',    # Gray secondary
            'card_bg': '#2a2a2a',      # Card background
            'button_bg': '#333333',    # Button background
            'button_fg': '#ffffff',    # Button text
            'high': '#ff4757',         # High priority red
            'medium': '#ffa726',       # Medium priority orange
            'low': '#26de81'           # Low priority green
        }
        
        self.tasks = []
        self.data_file = "tasks.json"
        self.load_tasks()
        self.setup_ui()
        self.root.mainloop()
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    task_data = json.load(f)
                    self.tasks = []
                    for task_dict in task_data:
                        task = ModernTask(
                            title=task_dict['title'],
                            description=task_dict.get('description', ''),
                            priority=task_dict.get('priority', 'Medium'),
                            status=task_dict.get('status', 'Active'),
                            due_date=task_dict.get('due_date')
                        )
                        task.id = task_dict.get('id', task.generate_id())
                        task.created_date = task_dict.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
                        task.completed_date = task_dict.get('completed_date')
                        self.tasks.append(task)
        except Exception as e:
            print(f"Note: Could not load tasks: {e}")
            self.tasks = []
    
    def save_tasks(self):
        """Save tasks to file"""
        try:
            task_data = [{
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date,
                'created_date': task.created_date,
                'completed_date': task.completed_date,
                'id': task.id
            } for task in self.tasks]
            
            with open(self.data_file, 'w') as f:
                json.dump(task_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tasks: {e}")
    
    def setup_ui(self):
        """Setup modern UI"""
        # Configure window
        self.root.configure(bg=self.colors['bg'])
        self.root.option_add('*Background', self.colors['bg'])
        self.root.option_add('*Foreground', self.colors['fg'])
        
        # Modern fonts
        self.title_font = ('Segoe UI', 24, 'bold')
        self.header_font = ('Segoe UI', 14, 'bold')
        self.body_font = ('Segoe UI', 12)
        self.small_font = ('Segoe UI', 10)
        
        # Title
        title_label = tk.Label(self.root, text="Modern Task Manager", 
                              font=self.title_font, fg=self.colors['accent'], 
                              bg=self.colors['bg'])
        title_label.pack(pady=10)
        
        # Search and filter frame
        filter_frame = tk.Frame(self.root, bg=self.colors['bg'])
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda name, index, mode: self.display_tasks())
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var,
                               font=self.body_font, bg=self.colors['card_bg'], 
                               fg=self.colors['fg'], insertbackground=self.colors['fg'],
                               relief='flat', bd=1)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        search_entry.insert(0, "Search tasks...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search tasks..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search tasks...") if not search_entry.get() else None)
        
        # Filter by status
        self.status_filter = tk.StringVar(value="All")
        status_combo = tk.OptionMenu(filter_frame, self.status_filter, "All", "Active", "Completed")
        status_combo.config(font=self.small_font, bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                           relief='flat', bd=1)
        status_combo.pack(side='left', padx=5)
        self.status_filter.trace('w', lambda name, index, mode: self.display_tasks())
        
        # Filter by priority
        self.priority_filter = tk.StringVar(value="All")
        priority_combo = tk.OptionMenu(filter_frame, self.priority_filter, "All", "High", "Medium", "Low")
        priority_combo.config(font=self.small_font, bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                             relief='flat', bd=1)
        priority_combo.pack(side='left', padx=5)
        self.priority_filter.trace('w', lambda name, index, mode: self.display_tasks())
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Task list
        left_panel = tk.Frame(main_container, bg=self.colors['card_bg'], 
                             relief='flat', bd=0)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Task list header
        list_header = tk.Frame(left_panel, bg=self.colors['card_bg'])
        list_header.pack(fill='x', padx=15, pady=15)
        
        list_title = tk.Label(list_header, text="Tasks", 
                             font=self.header_font, fg=self.colors['fg'], 
                             bg=self.colors['card_bg'])
        list_title.pack(side='left')
        
        add_button = tk.Button(list_header, text="+ Add Task", 
                              font=self.body_font, bg=self.colors['button_bg'], 
                              fg=self.colors['button_fg'], relief='flat', 
                              command=self.add_task, cursor='hand2')
        add_button.pack(side='right', padx=5)
        
        # Task list container
        self.task_container = tk.Frame(left_panel, bg=self.colors['card_bg'])
        self.task_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Right panel - Task details
        right_panel = tk.Frame(main_container, bg=self.colors['card_bg'], 
                              relief='flat', bd=0)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Details header
        details_header = tk.Frame(right_panel, bg=self.colors['card_bg'])
        details_header.pack(fill='x', padx=15, pady=15)
        
        details_title = tk.Label(details_header, text="Task Details", 
                                font=self.header_font, fg=self.colors['fg'], 
                                bg=self.colors['card_bg'])
        details_title.pack(side='left')
        
        # Task details form
        self.setup_task_form(right_panel)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors['bg'])
        status_frame.pack(fill='x', padx=20, pady=10)
        
        # Task statistics
        self.stats_label = tk.Label(status_frame, 
                                   text="", 
                                   font=self.small_font, 
                                   fg=self.colors['secondary'], 
                                   bg=self.colors['bg'])
        self.stats_label.pack(side='left')
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready", 
                                    font=self.small_font, 
                                    fg=self.colors['secondary'], 
                                    bg=self.colors['bg'])
        self.status_label.pack(side='right')
        
        # Load initial tasks
        self.display_tasks()
    
    def setup_task_form(self, parent):
        """Setup task detail form"""
        form_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        form_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Title
        tk.Label(form_frame, text="Title:", 
                font=self.body_font, fg=self.colors['fg'], 
                bg=self.colors['card_bg']).pack(anchor='w', pady=(0, 5))
        
        self.title_entry = tk.Entry(form_frame, font=self.body_font, 
                                   bg=self.colors['bg'], fg=self.colors['fg'], 
                                   insertbackground=self.colors['fg'])
        self.title_entry.pack(fill='x', pady=(0, 15))
        
        # Description
        tk.Label(form_frame, text="Description:", 
                font=self.body_font, fg=self.colors['fg'], 
                bg=self.colors['card_bg']).pack(anchor='w', pady=(10, 5))
        
        self.description_text = tk.Text(form_frame, font=self.body_font, 
                                       bg=self.colors['bg'], fg=self.colors['fg'], 
                                       insertbackground=self.colors['fg'], 
                                       height=4, relief='flat', bd=1)
        self.description_text.pack(fill='both', expand=True, pady=(0, 15))
        
        # Priority
        tk.Label(form_frame, text="Priority:", 
                font=self.body_font, fg=self.colors['fg'], 
                bg=self.colors['card_bg']).pack(anchor='w', pady=(10, 5))
        
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        priority_frame.pack(fill='x', pady=(0, 15))
        
        for priority in ["High", "Medium", "Low"]:
            rb = tk.Radiobutton(priority_frame, text=priority, variable=self.priority_var, 
                               value=priority, font=self.body_font, 
                               bg=self.colors['card_bg'], fg=self.colors['fg'], 
                               selectcolor=self.colors[priority.lower()], 
                               activebackground=self.colors['card_bg'], 
                               activeforeground=self.colors['fg'])
            rb.pack(side='left', padx=10)
        
        # Status
        tk.Label(form_frame, text="Status:", 
                font=self.body_font, fg=self.colors['fg'], 
                bg=self.colors['card_bg']).pack(anchor='w', pady=(10, 5))
        
        self.status_var = tk.StringVar(value="Active")
        status_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        status_frame.pack(fill='x', pady=(0, 15))
        
        for status in ["Active", "Completed"]:
            rb = tk.Radiobutton(status_frame, text=status, variable=self.status_var, 
                               value=status, font=self.body_font, 
                               bg=self.colors['card_bg'], fg=self.colors['fg'], 
                               selectcolor=self.colors['secondary'], 
                               activebackground=self.colors['card_bg'], 
                               activeforeground=self.colors['fg'])
            rb.pack(side='left', padx=10)
        
        # Due date
        tk.Label(form_frame, text="Due Date (YYYY-MM-DD):", 
                font=self.body_font, fg=self.colors['fg'], 
                bg=self.colors['card_bg']).pack(anchor='w', pady=(10, 5))
        
        self.due_date_entry = tk.Entry(form_frame, font=self.body_font, 
                                      bg=self.colors['bg'], fg=self.colors['fg'], 
                                      insertbackground=self.colors['fg'])
        self.due_date_entry.pack(fill='x', pady=(0, 20))
        
        # Action buttons
        button_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill='x', pady=(10, 0))
        
        save_button = tk.Button(button_frame, text="Save Task", 
                               font=self.body_font, bg=self.colors['accent'], 
                               fg=self.colors['bg'], relief='flat', 
                               command=self.save_task, cursor='hand2')
        save_button.pack(side='left', padx=5)
        
        clear_button = tk.Button(button_frame, text="Clear", 
                                font=self.body_font, bg=self.colors['button_bg'], 
                                fg=self.colors['button_fg'], relief='flat', 
                                command=self.clear_form, cursor='hand2')
        clear_button.pack(side='left', padx=5)
    
    def update_statistics(self):
        """Update task statistics"""
        total = len(self.tasks)
        active = len([t for t in self.tasks if t.status == "Active"])
        completed = len([t for t in self.tasks if t.status == "Completed"])
        high_priority = len([t for t in self.tasks if t.priority == "High"])
        
        self.stats_label.config(text=f"Total: {total} | Active: {active} | Completed: {completed} | High Priority: {high_priority}")
    
    def display_tasks(self):
        """Display filtered tasks in modern format"""
        # Update statistics
        self.update_statistics()
        
        # Clear existing tasks
        for widget in self.task_container.winfo_children():
            widget.destroy()
        
        # Apply filters
        filtered_tasks = self.tasks.copy()
        
        # Search filter
        search_text = self.search_var.get().lower()
        if search_text and search_text != "search tasks...":
            filtered_tasks = [task for task in filtered_tasks 
                            if search_text in task.title.lower() or 
                               search_text in task.description.lower()]
        
        # Status filter
        if self.status_filter.get() != "All":
            filtered_tasks = [task for task in filtered_tasks 
                            if task.status == self.status_filter.get()]
        
        # Priority filter
        if self.priority_filter.get() != "All":
            filtered_tasks = [task for task in filtered_tasks 
                            if task.priority == self.priority_filter.get()]
        
        if not filtered_tasks:
            no_tasks_label = tk.Label(self.task_container, 
                                     text="No tasks found matching your filters." if (search_text and search_text != "search tasks...") or self.status_filter.get() != "All" or self.priority_filter.get() != "All" else "No tasks yet. Add your first task!", 
                                     font=self.body_font, 
                                     fg=self.colors['secondary'], 
                                     bg=self.colors['card_bg'])
            no_tasks_label.pack(pady=50)
            return
        
        for i, task in enumerate(filtered_tasks, 1):
            task_card = tk.Frame(self.task_container, bg=self.colors['card_bg'], 
                                relief='flat', bd=1)
            task_card.pack(fill='x', padx=10, pady=8)
            
            # Task header
            header_frame = tk.Frame(task_card, bg=self.colors['card_bg'])
            header_frame.pack(fill='x', padx=15, pady=10)
            
            # Status icon
            status_icon = "✅" if task.status == "Completed" else "⏳"
            status_label = tk.Label(header_frame, text=status_icon, 
                                   font=('Segoe UI', 16), 
                                   fg=self.colors['accent'] if task.status == "Completed" else self.colors['secondary'], 
                                   bg=self.colors['card_bg'])
            status_label.pack(side='left', padx=(0, 10))
            
            # Task info
            info_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
            info_frame.pack(side='left', fill='x', expand=True)
            
            title_label = tk.Label(info_frame, text=task.title, 
                                  font=self.header_font, 
                                  fg=self.colors['fg'], 
                                  bg=self.colors['card_bg'])
            title_label.pack(anchor='w')
            
            if task.description:
                desc_label = tk.Label(info_frame, text=task.description[:100] + "..." if len(task.description) > 100 else task.description, 
                                     font=self.small_font, 
                                     fg=self.colors['secondary'], 
                                     bg=self.colors['card_bg'])
                desc_label.pack(anchor='w')
            
            # Priority badge
            priority_color = self.colors[task.priority.lower()]
            priority_label = tk.Label(header_frame, text=task.priority, 
                                     font=self.small_font, 
                                     fg=priority_color, 
                                     bg=self.colors['card_bg'])
            priority_label.pack(side='right', padx=10)
            
            # Action buttons
            button_frame = tk.Frame(task_card, bg=self.colors['card_bg'])
            button_frame.pack(fill='x', padx=15, pady=5)
            
            edit_button = tk.Button(button_frame, text="Edit", 
                                   font=self.small_font, 
                                   bg=self.colors['button_bg'], 
                                   fg=self.colors['button_fg'], 
                                   relief='flat', command=lambda t=task: self.edit_task(t), 
                                   cursor='hand2')
            edit_button.pack(side='left', padx=5)
            
            if task.status == "Active":
                complete_button = tk.Button(button_frame, text="Complete", 
                                           font=self.small_font, 
                                           bg=self.colors['accent'], 
                                           fg=self.colors['bg'], relief='flat', 
                                           command=lambda t=task: self.complete_task(t), 
                                           cursor='hand2')
                complete_button.pack(side='left', padx=5)
            
            delete_button = tk.Button(button_frame, text="Delete", 
                                     font=self.small_font, 
                                     bg='#ff4757', 
                                     fg='white', relief='flat', 
                                     command=lambda t=task: self.delete_task(t), 
                                     cursor='hand2')
            delete_button.pack(side='right', padx=5)
    
    def save_task(self):
        """Save current task (add new or update existing)"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title cannot be empty!")
            return
        
        # Check if we're editing an existing task
        current_task_title = self.title_entry.get().strip()
        existing_task = None
        for task in self.tasks:
            if task.title == current_task_title and task.created_date != datetime.now().strftime("%Y-%m-%d %H:%M"):
                existing_task = task
                break
        
        if existing_task:
            # Update existing task
            existing_task.title = title
            existing_task.description = self.description_text.get('1.0', tk.END).strip()
            existing_task.priority = self.priority_var.get()
            existing_task.status = self.status_var.get()
            existing_task.due_date = self.due_date_entry.get().strip() or None
            message = f"Task '{title}' updated successfully!"
        else:
            # Create new task
            task = ModernTask(
                title=title,
                description=self.description_text.get('1.0', tk.END).strip(),
                priority=self.priority_var.get(),
                status=self.status_var.get(),
                due_date=self.due_date_entry.get().strip() or None
            )
            self.tasks.append(task)
            message = f"Task '{title}' saved successfully!"
        
        self.save_tasks()
        self.display_tasks()
        self.clear_form()
        
        self.status_label.config(text=message)
    
    def edit_task(self, task):
        """Edit existing task"""
        # Populate form with task data
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, task.title)
        
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', task.description)
        
        self.priority_var.set(task.priority)
        self.status_var.set(task.status)
        self.due_date_entry.delete(0, tk.END)
        if task.due_date:
            self.due_date_entry.insert(0, task.due_date)
        
        self.status_label.config(text=f"Editing: {task.title}")
    
    def complete_task(self, task):
        """Mark task as completed"""
        task.status = "Completed"
        task.completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.save_tasks()
        self.display_tasks()
        self.status_label.config(text=f"Task '{task.title}' completed!")
    
    def delete_task(self, task):
        """Delete a task"""
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{task.title}'?")
        if result:
            self.tasks.remove(task)
            self.save_tasks()
            self.display_tasks()
            self.clear_form()
            self.status_label.config(text=f"Task '{task.title}' deleted successfully!")
    
    def add_task(self):
        """Add a new task"""
        self.save_task()  # Reuse the save_task method for adding new tasks
    
    def clear_form(self):
        """Clear the task form"""
        self.title_entry.delete(0, tk.END)
        self.description_text.delete('1.0', tk.END)
        self.priority_var.set("Medium")
        self.status_var.set("Active")
        self.due_date_entry.delete(0, tk.END)
        self.status_label.config(text="Ready")

def main():
    """Main function"""
    print("🚀 Starting Modern Task Manager...")
    print("="*50)
    print("Modern, minimalistic task management")
    print("="*50)
    
    app = ModernTaskManager()
    print("✅ Modern Task Manager started successfully!")

if __name__ == "__main__":
    main()