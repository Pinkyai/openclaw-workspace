#!/usr/bin/env python3
"""
Clean Task Manager - No external dependencies
Simple terminal-based task management
"""

import json
import os
from datetime import datetime, date

class Task:
    def __init__(self, title, description="", priority="Medium", status="Active", 
                 category="General", due_date=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.category = category
        self.due_date = due_date
        self.created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.completed_date = None
        self.id = self.generate_id()
    
    def generate_id(self):
        import uuid
        return str(uuid.uuid4())[:8]
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'due_date': self.due_date,
            'created_date': self.created_date,
            'completed_date': self.completed_date,
            'id': self.id
        }

class SimpleTaskManager:
    """Simple terminal-based task manager"""
    
    def __init__(self):
        self.tasks = []
        self.data_file = "tasks.json"
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    task_data = json.load(f)
                    self.tasks = []
                    for task_dict in task_data:
                        task = Task(
                            title=task_dict['title'],
                            description=task_dict.get('description', ''),
                            priority=task_dict.get('priority', 'Medium'),
                            status=task_dict.get('status', 'Active'),
                            category=task_dict.get('category', 'General'),
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
            task_data = [task.to_dict() for task in self.tasks]
            with open(self.data_file, 'w') as f:
                json.dump(task_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save tasks: {e}")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self):
        """Display application header"""
        print("\n" + "="*50)
        print("📋 SIMPLE TASK MANAGER")
        print("="*50)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
    
    def display_tasks(self):
        """Display all tasks"""
        if not self.tasks:
            print("\n📭 No tasks found!")
            return
        
        print(f"\n📊 TASKS ({len(self.tasks)} total)")
        print("-" * 70)
        
        for i, task in enumerate(self.tasks, 1):
            status_icon = "✅" if task.status == "Completed" else "⏳"
            priority_color = "🔴" if task.priority == "High" else "🟡" if task.priority == "Medium" else "🟢"
            
            print(f"\n{i}. {status_icon} {priority_color} {task.title}")
            print(f"   Status: {task.status} | Priority: {task.priority}")
            if task.description:
                print(f"   Description: {task.description}")
            if task.due_date:
                print(f"   Due: {task.due_date}")
            print(f"   Created: {task.created_date}")
    
    def add_task(self):
        """Add a new task"""
        print("\n➕ ADD NEW TASK")
        print("-" * 30)
        
        title = input("Task title: ").strip()
        if not title:
            print("❌ Title cannot be empty!")
            return
        
        description = input("Description (optional): ").strip()
        priority = input("Priority (High/Medium/Low) [Medium]: ").strip() or "Medium"
        category = input("Category [General]: ").strip() or "General"
        due_date = input("Due date (YYYY-MM-DD, optional): ").strip() or None
        
        task = Task(title, description, priority, category, due_date)
        self.tasks.append(task)
        self.save_tasks()
        
        print(f"✅ Task '{title}' added successfully!")
    
    def edit_task(self):
        """Edit an existing task"""
        self.display_tasks()
        
        if not self.tasks:
            return
        
        try:
            task_num = int(input("\nEnter task number to edit: ")) - 1
            if 0 <= task_num < len(self.tasks):
                task = self.tasks[task_num]
                
                print(f"\n✏️ EDITING: {task.title}")
                print("Press Enter to keep current value")
                
                title = input(f"Title [{task.title}]: ").strip() or task.title
                description = input(f"Description [{task.description}]: ").strip() or task.description
                priority = input(f"Priority [{task.priority}]: ").strip() or task.priority
                status = input(f"Status [{task.status}]: ").strip() or task.status
                category = input(f"Category [{task.category}]: ").strip() or task.category
                due_date = input(f"Due date [{task.due_date or 'None'}]: ").strip() or task.due_date
                
                task.title = title
                task.description = description
                task.priority = priority
                task.status = status
                task.category = category
                task.due_date = due_date if due_date != 'None' else None
                
                self.save_tasks()
                print(f"✅ Task '{title}' updated successfully!")
            else:
                print("❌ Invalid task number!")
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def delete_task(self):
        """Delete a task"""
        self.display_tasks()
        
        if not self.tasks:
            return
        
        try:
            task_num = int(input("\nEnter task number to delete: ")) - 1
            if 0 <= task_num < len(self.tasks):
                task = self.tasks[task_num]
                confirm = input(f"Delete '{task.title}'? (y/N): ").lower()
                
                if confirm == 'y':
                    self.tasks.remove(task)
                    self.save_tasks()
                    print(f"✅ Task '{task.title}' deleted successfully!")
                else:
                    print("❌ Deletion cancelled.")
            else:
                print("❌ Invalid task number!")
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def main_menu(self):
        """Display main menu"""
        while True:
            self.clear_screen()
            self.display_header()
            
            # Show task count
            active_tasks = len([t for t in self.tasks if t.status == "Active"])
            completed_tasks = len([t for t in self.tasks if t.status == "Completed"])
            print(f"📊 Active: {active_tasks} | Completed: {completed_tasks}")
            
            print("\n📋 MAIN MENU")
            print("-" * 30)
            print("1. 📋 View all tasks")
            print("2. ➕ Add new task")
            print("3. ✏️ Edit task")
            print("4. 🗑️ Delete task")
            print("5. 💾 Save & Exit")
            print("-" * 30)
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                self.display_tasks()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.add_task()
                input("\nPress Enter to continue...")
            elif choice == '3':
                self.edit_task()
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.delete_task()
                input("\nPress Enter to continue...")
            elif choice == '5':
                self.save_tasks()
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice! Please try again.")
                input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🚀 Starting Simple Task Manager...")
    manager = SimpleTaskManager()
    manager.main_menu()

if __name__ == "__main__":
    main()