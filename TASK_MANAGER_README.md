# Modern Task Manager 🚀

A beautiful, modern task management application with a sleek dark theme and comprehensive functionality.

## Features ✨

### Core Functionality
- **Task Management**: Create, edit, delete, and complete tasks
- **Task Properties**: Title, description, priority, status, due date
- **Smart Filtering**: Filter by status (Active/Completed) and priority (High/Medium/Low)
- **Search Functionality**: Search tasks by title and description
- **Data Persistence**: Automatic saving and loading of tasks
- **Task Statistics**: Real-time statistics display

### User Interface
- **Modern Dark Theme**: Sleek, eye-friendly dark interface
- **Responsive Design**: Clean and intuitive layout
- **Color-Coded Priorities**: Visual priority indicators
- **Status Indicators**: Clear task status visualization
- **Smooth Animations**: Professional user experience

### Advanced Features
- **Form Validation**: Input validation and error handling
- **Task Completion Tracking**: Automatic completion timestamp
- **Persistent Storage**: JSON-based data storage
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation 📦

### Requirements
- Python 3.6 or higher
- tkinter (usually included with Python)

### Setup
1. Clone or download the repository
2. Ensure Python 3.6+ is installed
3. Run the application:

```bash
python3 final_task_manager.py
```

## Usage Guide 📖

### Getting Started
1. Launch the application
2. The main window will appear with your task list
3. Use the search bar to find specific tasks
4. Apply filters to focus on specific task types

### Creating Tasks
1. Fill in the task details in the right panel
2. Enter a title (required)
3. Add a description (optional)
4. Set priority level (High, Medium, Low)
5. Set status (Active, Completed)
6. Add due date (optional, format: YYYY-MM-DD)
7. Click "Save Task" to create the task

### Managing Tasks
- **Edit**: Click the "Edit" button on any task card
- **Complete**: Click "Complete" to mark active tasks as done
- **Delete**: Click "Delete" to remove a task (with confirmation)
- **Search**: Use the search bar to find tasks quickly
- **Filter**: Use dropdown menus to filter by status and priority

### Task Statistics
The status bar shows real-time statistics:
- Total number of tasks
- Active tasks count
- Completed tasks count
- High priority tasks count

## Technical Details 🔧

### Architecture
- **Language**: Python 3.6+
- **GUI Framework**: tkinter
- **Data Storage**: JSON file (`tasks.json`)
- **Design Pattern**: Model-View-Controller (MVC)

### File Structure
```
final_task_manager.py    # Main application file
tasks.json              # Task data storage
test_task_manager.py    # Functionality test script
README.md               # This documentation
```

### Data Model
Each task contains:
```json
{
  "title": "Task title",
  "description": "Task description",
  "priority": "High|Medium|Low",
  "status": "Active|Completed",
  "due_date": "YYYY-MM-DD",
  "created_date": "YYYY-MM-DD HH:MM",
  "completed_date": "YYYY-MM-DD HH:MM",
  "id": "unique-task-id"
}
```

## Customization 🎨

### Color Scheme
The application uses a modern dark theme with customizable colors:
- Background: `#1a1a1a`
- Text: `#ffffff`
- Accent: `#00ff88`
- High Priority: `#ff4757`
- Medium Priority: `#ffa726`
- Low Priority: `#26de81`

### Fonts
- Title: Segoe UI, 24pt, Bold
- Headers: Segoe UI, 14pt, Bold
- Body: Segoe UI, 12pt
- Small: Segoe UI, 10pt

## Troubleshooting 🔧

### Common Issues
1. **Application won't start**: Ensure Python 3.6+ is installed
2. **GUI not displaying**: Check if tkinter is properly installed
3. **Tasks not saving**: Verify write permissions in the application directory
4. **Search not working**: Ensure you're entering valid search terms

### Data Recovery
Tasks are automatically saved to `tasks.json`. If the file becomes corrupted:
1. Make a backup of the corrupted file
2. Delete or rename the corrupted file
3. Restart the application to create a fresh data file

## Future Enhancements 🚀

Potential features for future versions:
- **Categories/Tags**: Organize tasks by categories
- **Due Date Reminders**: Notification system for approaching deadlines
- **Task Templates**: Predefined task templates
- **Export/Import**: Backup and restore functionality
- **Dark/Light Theme Toggle**: Theme switching capability
- **Task Dependencies**: Link related tasks
- **Progress Tracking**: Task completion percentage
- **Mobile App**: Companion mobile application

## Contributing 🤝

Feel free to contribute to this project by:
1. Reporting bugs and issues
2. Suggesting new features
3. Submitting pull requests
4. Improving documentation

## License 📄

This project is open source and available under the MIT License.

## Support 💬

For support and questions:
1. Check the troubleshooting section
2. Review the technical documentation
3. Test functionality with the included test script

---

**Made with ❤️ for better task management**