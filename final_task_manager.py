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
        title_label.pack(pady=20)
        
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
        
        self.status_label = tk.Label(status_frame, 
                                    text="Ready", 
                                    font=self.small_font, 
                                    fg=self.colors['secondary'], 
                                    bg=self.colors['bg'])
        self.status_label.pack()
        
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
    
    def display_tasks(self):
        """Display all tasks in modern format"""
        # Clear existing tasks
        for widget in self.task_container.winfo_children():
            widget.destroy()
        
        if not self.tasks:
            no_tasks_label = tk.Label(self.task_container, 
                                     text="No tasks yet. Add your first task!", 
                                     font=self.body_font, 
                                     fg=self.colors['secondary'], 
                                     bg=self.colors['card_bg'])
            no_tasks_label.pack(pady=50)
            return
        
        for i, task in enumerate(self.tasks, 1):
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
    
    def save_task(self):
        """Save current task"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Title cannot be empty!")
            return
        
        # Create new task
        task = ModernTask(
            title=title,
            description=self.description_text.get('1.0', tk.END).strip(),
            priority=self.priority_var.get(),
            status=self.status_var.get(),
            due_date=self.due_date_entry.get().strip() or None
        )
        
        self.tasks.append(task)
        self.save_tasks()
        self.display_tasks()
        self.clear_form()
        
        self.status_label.config(text=f"Task '{title}' saved successfully!")
    
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