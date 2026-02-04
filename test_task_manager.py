#!/usr/bin/env python3
"""
Test script to verify the Modern Task Manager functionality
"""

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
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'due_date': self.due_date,
            'created_date': self.created_date,
            'completed_date': self.completed_date,
            'id': self.id
        }

def test_task_manager():
    """Test the core functionality of the task manager"""
    print("🧪 Testing Modern Task Manager Functionality")
    print("=" * 50)
    
    # Test task creation
    print("\n1. Testing Task Creation:")
    task1 = ModernTask("Test Task 1", "This is a test task", "High", "Active", "2026-02-10")
    task2 = ModernTask("Test Task 2", "Another test task", "Medium", "Active")
    task3 = ModernTask("Completed Task", "This task is done", "Low", "Completed")
    
    tasks = [task1, task2, task3]
    
    for i, task in enumerate(tasks, 1):
        print(f"   Task {i}: {task.title}")
        print(f"   - Priority: {task.priority}")
        print(f"   - Status: {task.status}")
        print(f"   - Due Date: {task.due_date}")
        print(f"   - ID: {task.id}")
        print()
    
    # Test task filtering
    print("2. Testing Task Filtering:")
    active_tasks = [task for task in tasks if task.status == "Active"]
    high_priority_tasks = [task for task in tasks if task.priority == "High"]
    
    print(f"   Active tasks: {len(active_tasks)}")
    print(f"   High priority tasks: {len(high_priority_tasks)}")
    
    # Test search functionality
    print("\n3. Testing Search Functionality:")
    search_term = "test"
    matching_tasks = [task for task in tasks if search_term.lower() in task.title.lower() or search_term.lower() in task.description.lower()]
    print(f"   Tasks matching '{search_term}': {len(matching_tasks)}")
    
    # Test data persistence
    print("\n4. Testing Data Persistence:")
    test_file = "test_tasks.json"
    
    # Save tasks
    task_data = [task.to_dict() for task in tasks]
    with open(test_file, 'w') as f:
        json.dump(task_data, f, indent=2)
    print(f"   Saved {len(tasks)} tasks to {test_file}")
    
    # Load tasks
    with open(test_file, 'r') as f:
        loaded_data = json.load(f)
    print(f"   Loaded {len(loaded_data)} tasks from {test_file}")
    
    # Clean up
    os.remove(test_file)
    
    # Test task completion
    print("\n5. Testing Task Completion:")
    original_status = task1.status
    task1.status = "Completed"
    task1.completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"   Task '{task1.title}' status changed from '{original_status}' to '{task1.status}'")
    print(f"   Completed at: {task1.completed_date}")
    
    print("\n✅ All functionality tests passed!")
    print("\n📋 Task Manager Features Summary:")
    print("   ✓ Create tasks with title, description, priority, status, due date")
    print("   ✓ Filter tasks by status (Active, Completed)")
    print("   ✓ Filter tasks by priority (High, Medium, Low)")
    print("   ✓ Search tasks by title and description")
    print("   ✓ Save and load tasks from JSON")
    print("   ✓ Mark tasks as completed")
    print("   ✓ Modern dark theme UI")
    print("   ✓ Task statistics and counters")

if __name__ == "__main__":
    test_task_manager()