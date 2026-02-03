class TodoApp {
    constructor() {
        this.tasks = [];
        this.currentFilter = 'all';
        this.taskIdCounter = 0;
        
        this.initializeElements();
        this.loadTasks();
        this.bindEvents();
        this.render();
    }

    initializeElements() {
        this.elements = {
            taskForm: document.getElementById('task-form'),
            taskInput: document.getElementById('task-input'),
            categorySelect: document.getElementById('category-select'),
            tagInput: document.getElementById('tag-input'),
            tasksContainer: document.getElementById('tasks-container'),
            emptyState: document.getElementById('empty-state'),
            searchInput: document.getElementById('search-input'),
            completedCount: document.getElementById('completed-count'),
            totalCount: document.getElementById('total-count'),
            clearCompleted: document.getElementById('clear-completed'),
            exportTasks: document.getElementById('export-tasks'),
            importTasks: document.getElementById('import-tasks'),
            importFile: document.getElementById('import-file'),
            filterBtns: document.querySelectorAll('.filter-btn')
        };
    }

    bindEvents() {
        this.elements.taskForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.elements.searchInput.addEventListener('input', () => this.render());
        this.elements.clearCompleted.addEventListener('click', () => this.clearCompleted());
        this.elements.exportTasks.addEventListener('click', () => this.exportTasks());
        this.elements.importTasks.addEventListener('click', () => this.elements.importFile.click());
        this.elements.importFile.addEventListener('change', (e) => this.importTasks(e));
        
        this.elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', () => this.setFilter(btn.dataset.filter));
        });

        // Dark mode toggle
        const darkModeToggle = document.createElement('button');
        darkModeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        darkModeToggle.className = 'dark-mode-toggle';
        darkModeToggle.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 0.75rem;
            cursor: pointer;
            color: var(--text-primary);
            transition: var(--transition);
            z-index: 1000;
        `;
        
        darkModeToggle.addEventListener('click', () => this.toggleDarkMode());
        document.body.appendChild(darkModeToggle);

        // Load dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.documentElement.setAttribute('data-theme', 'dark');
            darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        
        const taskText = this.elements.taskInput.value.trim();
        if (!taskText) return;

        const task = {
            id: ++this.taskIdCounter,
            text: taskText,
            completed: false,
            category: this.elements.categorySelect.value,
            tags: this.elements.tagInput.value.split(',').map(tag => tag.trim()).filter(tag => tag),
            createdAt: new Date().toISOString(),
            completedAt: null
        };

        this.tasks.unshift(task);
        this.saveTasks();
        this.render();
        
        // Reset form
        this.elements.taskForm.reset();
        this.elements.categorySelect.value = '';
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            this.saveTasks();
            this.render();
        }
    }

    deleteTask(id) {
        const taskElement = document.querySelector(`[data-task-id="${id}"]`);
        if (taskElement) {
            taskElement.classList.add('removing');
            setTimeout(() => {
                this.tasks = this.tasks.filter(t => t.id !== id);
                this.saveTasks();
                this.render();
            }, 300);
        }
    }

    setFilter(filter) {
        this.currentFilter = filter;
        this.elements.filterBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        this.render();
    }

    getFilteredTasks() {
        let filtered = this.tasks;

        // Apply filter
        if (this.currentFilter === 'active') {
            filtered = filtered.filter(task => !task.completed);
        } else if (this.currentFilter === 'completed') {
            filtered = filtered.filter(task => task.completed);
        }

        // Apply search
        const searchTerm = this.elements.searchInput.value.toLowerCase();
        if (searchTerm) {
            filtered = filtered.filter(task => 
                task.text.toLowerCase().includes(searchTerm) ||
                task.tags.some(tag => tag.toLowerCase().includes(searchTerm))
            );
        }

        return filtered;
    }

    render() {
        const filteredTasks = this.getFilteredTasks();
        
        // Update stats
        const completedCount = this.tasks.filter(t => t.completed).length;
        this.elements.completedCount.textContent = completedCount;
        this.elements.totalCount.textContent = this.tasks.length;

        // Show/hide empty state
        this.elements.emptyState.classList.toggle('show', filteredTasks.length === 0);

        // Render tasks
        this.elements.tasksContainer.innerHTML = filteredTasks.map(task => this.createTaskHTML(task)).join('');

        // Bind task events
        this.elements.tasksContainer.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleTask(parseInt(checkbox.dataset.taskId));
            });
        });

        this.elements.tasksContainer.querySelectorAll('.delete-task').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteTask(parseInt(btn.dataset.taskId));
            });
        });

        this.elements.tasksContainer.querySelectorAll('.task-item').forEach(item => {
            item.addEventListener('click', () => {
                this.toggleTask(parseInt(item.dataset.taskId));
            });
        });
    }

    createTaskHTML(task) {
        const categoryClass = task.category ? `category-${task.category}` : '';
        const categoryLabel = task.category ? task.category.charAt(0).toUpperCase() + task.category.slice(1) : '';
        const createdDate = new Date(task.createdAt).toLocaleDateString();
        
        return `
            <div class="task-item ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
                <div class="task-checkbox ${task.completed ? 'checked' : ''}" data-task-id="${task.id}">
                    ${task.completed ? '<i class="fas fa-check"></i>' : ''}
                </div>
                <div class="task-content">
                    <div class="task-text">${this.escapeHtml(task.text)}</div>
                    <div class="task-meta-info">
                        ${task.category ? `<span class="task-category ${categoryClass}">${categoryLabel}</span>` : ''}
                        ${task.tags.length > 0 ? `<div class="task-tags">${task.tags.map(tag => `<span class="task-tag">${this.escapeHtml(tag)}</span>`).join('')}</div>` : ''}
                        <span class="task-time">${createdDate}</span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-action-btn delete-task" data-task-id="${task.id}" title="Delete task">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    clearCompleted() {
        if (confirm('Are you sure you want to clear all completed tasks?')) {
            this.tasks = this.tasks.filter(t => !t.completed);
            this.saveTasks();
            this.render();
        }
    }

    exportTasks() {
        const data = {
            tasks: this.tasks,
            exportedAt: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `todo-backup-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    importTasks(e) {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                if (data.tasks && Array.isArray(data.tasks)) {
                    if (confirm(`Import ${data.tasks.length} tasks? This will merge with existing tasks.`)) {
                        // Merge tasks and remove duplicates based on text
                        const existingTexts = new Set(this.tasks.map(t => t.text));
                        const newTasks = data.tasks.filter(t => !existingTexts.has(t.text));
                        
                        this.tasks = [...this.tasks, ...newTasks];
                        this.saveTasks();
                        this.render();
                        
                        alert(`Successfully imported ${newTasks.length} new tasks!`);
                    }
                } else {
                    alert('Invalid file format!');
                }
            } catch (error) {
                alert('Error reading file!');
            }
        };
        reader.readAsText(file);
        
        // Reset file input
        e.target.value = '';
    }

    toggleDarkMode() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (isDark) {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('darkMode', 'false');
            document.querySelector('.dark-mode-toggle').innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('darkMode', 'true');
            document.querySelector('.dark-mode-toggle').innerHTML = '<i class="fas fa-sun"></i>';
        }
    }

    saveTasks() {
        localStorage.setItem('todoTasks', JSON.stringify(this.tasks));
        localStorage.setItem('taskIdCounter', this.taskIdCounter.toString());
    }

    loadTasks() {
        const saved = localStorage.getItem('todoTasks');
        const savedCounter = localStorage.getItem('taskIdCounter');
        
        if (saved) {
            try {
                this.tasks = JSON.parse(saved);
            } catch (e) {
                this.tasks = [];
            }
        }
        
        if (savedCounter) {
            this.taskIdCounter = parseInt(savedCounter) || 0;
        }
    }
}

// Additional CSS for dark mode toggle
const additionalCSS = `
.dark-mode-toggle:hover {
    background: var(--primary-color) !important;
    color: white !important;
    border-color: var(--primary-color) !important;
}

@media (max-width: 768px) {
    .dark-mode-toggle {
        top: auto;
        bottom: 1rem;
        right: 1rem;
    }
}
`;

// Inject additional CSS
const style = document.createElement('style');
style.textContent = additionalCSS;
document.head.appendChild(style);

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new TodoApp();
});