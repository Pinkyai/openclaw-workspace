# Task Manager Pro

A comprehensive task management application built with Python and tkinter.

## Features

✅ **Task Management**
- Create, edit, and delete tasks
- Task titles and descriptions
- Status tracking (To Do, In Progress, Done)
- Priority levels (High, Medium, Low)
- Progress bars (0-100%)
- Due dates
- Categories (Personal, Work, Shopping, Health, Other)

✅ **User Interface**
- Modern, clean design
- Intuitive task form
- Sortable task list with columns
- Color-coded priorities
- Search and filter functionality
- Context menu (right-click)
- Double-click to toggle status

✅ **Data Management**
- Automatic JSON save/load
- Export to JSON/CSV
- Import from JSON/CSV
- Persistent storage

✅ **Advanced Features**
- Search across titles and descriptions
- Filter by status and category
- Sort by priority and due date
- Progress tracking
- Professional error handling

## Usage

### Quick Start
```bash
# Make executable and run
chmod +x start_task_manager.sh
./start_task_manager.sh

# Or run directly
python3 task_manager_gui.py
```

### Adding Tasks
1. Fill in the task form on the left
2. Set title (required), description, category, priority
3. Choose due date and progress percentage
4. Click "Add Task"

### Managing Tasks
- **Edit**: Select task from list, modify form, click "Update Task"
- **Delete**: Right-click task → "Delete Task" or select and press Delete
- **Status**: Double-click task to cycle through To Do → In Progress → Done
- **Search**: Type in search box to filter tasks
- **Filter**: Use dropdown filters for status and category

### Data Operations
- **Export**: File → Export Tasks (JSON or CSV)
- **Import**: File → Import Tasks (JSON or CSV)
- **Auto-save**: Tasks automatically save to `tasks.json`

## Keyboard Shortcuts
- **Enter**: Add new task (when form is filled)
- **Delete**: Delete selected task
- **Double-click**: Toggle task status
- **Right-click**: Context menu

## File Structure
```
task_manager_gui.py      # Main application
start_task_manager.sh    # Launcher script
tasks.json              # Task data (auto-created)
README.md               # This file
```

## Customization

### Adding New Categories
Edit the `values` parameter in the category combobox:
```python
category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                             values=["Personal", "Work", "Shopping", "Health", "YourCategory"])
```

### Changing Colors
Modify the `self.colors` dictionary in the `setup_styles()` method:
```python
self.colors = {
    'bg': '#f8f9fa',
    'fg': '#2c3e50',
    'accent': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c'
}
```

## Troubleshooting

### Application won't start
- Ensure Python 3.6+ is installed
- Install required modules: `pip install tkinter` (usually pre-installed)
- Check file permissions: `chmod +x task_manager_gui.py`

### Tasks not saving
- Check write permissions in the application directory
- Ensure `tasks.json` is not corrupted
- Look for error messages in the console

### Interface issues
- Try resizing the window
- Reset window position by deleting any saved preferences
- Check display scaling settings

## Technical Details

- **Framework**: Python 3.6+ with tkinter
- **Storage**: JSON file format
- **Architecture**: Object-oriented design
- **Error Handling**: Comprehensive try-catch blocks
- **Memory**: Efficient data structures
- **Performance**: Optimized for large task lists

## Future Enhancements
- [ ] Calendar integration
- [ ] Task reminders/notifications  
- [ ] Task templates
- [ ] Recurring tasks
- [ ] Task dependencies
- [ ] Time tracking
- [ ] Reports and analytics
- [ ] Cloud sync
- [ ] Mobile app companion

---

**Enjoy managing your tasks with Task Manager Pro!** 🚀