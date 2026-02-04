#!/usr/bin/env python3
"""
Task Manager Launcher
Easy launcher for the Modern Task Manager application
"""

import subprocess
import sys
import os

def launch_task_manager():
    """Launch the Modern Task Manager application"""
    print("🚀 Launching Modern Task Manager...")
    print("=" * 40)
    
    # Check if Python is available
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python version: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error checking Python version: {e}")
        return False
    
    # Check if the task manager file exists
    task_manager_file = "final_task_manager.py"
    if not os.path.exists(task_manager_file):
        print(f"❌ Task manager file '{task_manager_file}' not found!")
        return False
    
    print(f"✅ Found task manager: {task_manager_file}")
    
    # Launch the application
    try:
        print("🎯 Starting application...")
        subprocess.run([sys.executable, task_manager_file])
        return True
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
        return True
    except Exception as e:
        print(f"❌ Error launching application: {e}")
        return False

def show_help():
    """Show help information"""
    print("""
📋 Modern Task Manager Launcher

Usage:
    python launch_task_manager.py    - Launch the task manager
    python launch_task_manager.py -h - Show this help
    python launch_task_manager.py -t - Run functionality tests

Options:
    -h, --help     Show this help message
    -t, --test     Run functionality tests first
    -v, --version  Show version information

Features:
    ✓ Modern dark theme interface
    ✓ Create, edit, delete tasks
    ✓ Priority and status management
    ✓ Search and filter capabilities
    ✓ Automatic data persistence
    ✓ Task statistics and counters
    
Requirements:
    ✓ Python 3.6 or higher
    ✓ tkinter (usually included with Python)
""")

def run_tests():
    """Run functionality tests"""
    print("🧪 Running functionality tests...")
    try:
        result = subprocess.run([sys.executable, "test_task_manager.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print(f"❌ Tests failed with return code: {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-h', '--help']:
            show_help()
        elif arg in ['-t', '--test']:
            if run_tests():
                print("\n🚀 Launching task manager after successful tests...")
                launch_task_manager()
        elif arg in ['-v', '--version']:
            print("Modern Task Manager v1.0.0")
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("Use -h or --help for usage information")
    else:
        launch_task_manager()

if __name__ == "__main__":
    main()