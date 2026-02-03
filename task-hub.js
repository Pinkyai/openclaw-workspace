class TaskHub {
    constructor() {
        this.tasks = [];
        this.aiNotes = [];
        this.taskIdCounter = 0;
        
        this.initializeElements();
        this.loadTasks();
        this.bindEvents();
        this.render();
        this.startAutoRefresh();
    }

    initializeElements() {
        this.elements = {
            taskForm: document.getElementById('task-form'),
            taskInput: document.getElementById('task-input'),
            prioritySelect: document.getElementById('priority-select'),
            categoryInput: document.getElementById('category-input'),
            activeTasks: document.getElementById('active-tasks'),
            completedTasks: document.getElementById('completed-tasks'),
            noActiveTasks: document.getElementById('no-active-tasks'),
            noCompletedTasks: document.getElementById('no-completed-tasks'),
            activeCount: document.getElementById('active-count'),
            completedCount: document.getElementById('completed-count'),
            totalCount: document.getElementById('total-count'),
            lastUpdate: document.getElementById('last-update'),
            refreshBtn: document.getElementById('refresh-btn'),
            clearCompleted: document.getElementById('clear-completed'),
            aiNotes: document.getElementById('ai-notes')
        };
    }

    bindEvents() {
        this.elements.taskForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.elements.refreshBtn.addEventListener('click', () => this.refresh());
        this.elements.clearCompleted.addEventListener('click', () => this.clearCompleted());
        
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
            priority: this.elements.prioritySelect.value,
            category: this.elements.categoryInput.value.trim(),
            createdAt: new Date().toISOString(),
            completedAt: null,
            aiNotes: []
        };

        this.tasks.unshift(task);
        this.saveTasks();
        this.render();
        
        // Add AI note about new task
        this.addAINote(`Added new task: "${task.text}"${task.category ? ` in ${task.category} category` : ''}. I'll help you track this!`);
        
        // Reset form
        this.elements.taskForm.reset();
        this.elements.prioritySelect.value = 'medium';
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            
            if (task.completed) {
                this.addAINote(`Great job completing "${task.text}"! 🎉 One more task down!`);
            }
            
            this.saveTasks();
            this.render();
        }
    }

    deleteTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task && confirm(`Delete task: "${task.text}"?`)) {
            const taskElement = document.querySelector(`[data-task-id="${id}"]`);
            if (taskElement) {
                taskElement.classList.add('removing');
                setTimeout(() => {
                    this.tasks = this.tasks.filter(t => t.id !== id);
                    this.saveTasks();
                    this.render();
                    this.addAINote(`Removed task: "${task.text}"`);
                }, 300);
            }
        }
    }

    refresh() {
        this.render();
        this.updateLastUpdateTime();
        this.addAINote("Refreshed task list - everything looks good! 👍");
        
        // Visual feedback
        this.elements.refreshBtn.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            this.elements.refreshBtn.style.transform = '';
        }, 300);
    }

    clearCompleted() {
        const completedCount = this.tasks.filter(t => t.completed).length;
        if (completedCount === 0) return;
        
        if (confirm(`Clear all ${completedCount} completed tasks?`)) {
            this.tasks = this.tasks.filter(t => !t.completed);
            this.saveTasks();
            this.render();
            this.addAINote(`Cleared ${completedCount} completed tasks. Ready for new challenges! 🚀`);
        }
    }

    addAINote(text) {
        const note = {
            id: Date.now(),
            text: text,
            timestamp: new Date().toISOString()
        };
        
        this.aiNotes.unshift(note);
        
        // Keep only recent notes (last 10)
        if (this.aiNotes.length > 10) {
            this.aiNotes = this.aiNotes.slice(0, 10);
        }
        
        this.renderAINotes();
        this.saveTasks();
    }

    render() {
        this.renderStats();
        this.renderTasks();
        this.renderAINotes();
        this.updateLastUpdateTime();
    }

    renderStats() {
        const active = this.tasks.filter(t => !t.completed).length;
        const completed = this.tasks.filter(t => t.completed).length;
        const total = this.tasks.length;
        
        this.elements.activeCount.textContent = active;
        this.elements.completedCount.textContent = completed;
        this.elements.totalCount.textContent = total;
        
        // Animate number changes
        this.animateNumber(this.elements.activeCount, active);
        this.animateNumber(this.elements.completedCount, completed);
        this.animateNumber(this.elements.totalCount, total);
    }

    animateNumber(element, target) {
        const current = parseInt(element.textContent) || 0;
        if (current === target) return;
        
        const increment = target > current ? 1 : -1;
        const steps = Math.abs(target - current);
        const stepTime = 20;
        
        let step = 0;
        const timer = setInterval(() => {
            step++;
            const newValue = current + (increment * step);
            element.textContent = newValue;
            
            if (step >= steps) {
                clearInterval(timer);
                element.textContent = target;
            }
        }, stepTime);
    }

    renderTasks() {
        const activeTasks = this.tasks.filter(t => !t.completed);
        const completedTasks = this.tasks.filter(t => t.completed).slice(0, 10); // Show last 10 completed
        
        // Render active tasks
        this.elements.activeTasks.innerHTML = activeTasks.map(task => this.createTaskHTML(task)).join('');
        this.elements.noActiveTasks.classList.toggle('show', activeTasks.length === 0);
        
        // Render completed tasks
        this.elements.completedTasks.innerHTML = completedTasks.map(task => this.createTaskHTML(task)).join('');
        this.elements.noCompletedTasks.classList.toggle('show', completedTasks.length === 0);
        
        // Bind task events
        this.bindTaskEvents();
    }

    createTaskHTML(task) {
        const priorityClass = `priority-${task.priority}`;
        const createdDate = new Date(task.createdAt).toLocaleDateString();
        const timeAgo = this.getTimeAgo(task.createdAt);
        
        return `
            <div class="task-item ${task.completed ? 'completed' : ''}" data-task-id="${task.id}">
                <div class="task-checkbox ${task.completed ? 'checked' : ''}" data-task-id="${task.id}">
                    ${task.completed ? '<i class="fas fa-check"></i>' : ''}
                </div>
                <div class="task-content">
                    <div class="task-text">${this.escapeHtml(task.text)}</div>
                    <div class="task-meta">
                        <span class="task-priority ${priorityClass}">${task.priority}</span>
                        ${task.category ? `<span class="task-category">${this.escapeHtml(task.category)}</span>` : ''}
                        <span class="task-time">${timeAgo}</span>
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

    renderAINotes() {
        if (this.aiNotes.length === 0) {
            this.elements.aiNotes.innerHTML = `
                <div class="note-item">
                    <i class="fas fa-robot"></i>
                    <div class="note-content">
                        <p>Ready to help you tackle your tasks! I'm particularly excited about the trading platform project - that's going to be fun to build. 🚀</p>
                        <small>Just now</small>
                    </div>
                </div>
            `;
            return;
        }
        
        this.elements.aiNotes.innerHTML = this.aiNotes.map(note => `
            <div class="note-item">
                <i class="fas fa-robot"></i>
                <div class="note-content">
                    <p>${this.escapeHtml(note.text)}</p>
                    <small>${this.getTimeAgo(note.timestamp)}</small>
                </div>
            </div>
        `).join('');
    }

    bindTaskEvents() {
        // Checkbox clicks
        this.elements.activeTasks.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleTask(parseInt(checkbox.dataset.taskId));
            });
        });
        
        this.elements.completedTasks.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleTask(parseInt(checkbox.dataset.taskId));
            });
        });

        // Delete buttons
        document.querySelectorAll('.delete-task').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteTask(parseInt(btn.dataset.taskId));
            });
        });
    }

    getTimeAgo(timestamp) {
        const now = new Date();
        const past = new Date(timestamp);
        const diffMs = now - past;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return past.toLocaleDateString();
    }

    updateLastUpdateTime() {
        this.elements.lastUpdate.textContent = 'Just now';
        
        // Update every minute
        if (this.updateTimer) clearInterval(this.updateTimer);
        this.updateTimer = setInterval(() => {
            this.elements.lastUpdate.textContent = this.getTimeAgo(new Date().toISOString());
        }, 60000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
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

    startAutoRefresh() {
        // Refresh every 5 minutes to show updated times
        setInterval(() => {
            this.updateLastUpdateTime();
            this.renderAINotes(); // Update timeago for AI notes
        }, 300000);
    }

    saveTasks() {
        localStorage.setItem('taskHubTasks', JSON.stringify(this.tasks));
        localStorage.setItem('taskHubAINotes', JSON.stringify(this.aiNotes));
        localStorage.setItem('taskHubCounter', this.taskIdCounter.toString());
    }

    loadTasks() {
        const savedTasks = localStorage.getItem('taskHubTasks');
        const savedNotes = localStorage.getItem('taskHubAINotes');
        const savedCounter = localStorage.getItem('taskHubCounter');
        
        if (savedTasks) {
            try {
                this.tasks = JSON.parse(savedTasks);
            } catch (e) {
                this.tasks = [];
            }
        }
        
        if (savedNotes) {
            try {
                this.aiNotes = JSON.parse(savedNotes);
            } catch (e) {
                this.aiNotes = [];
            }
        }
        
        if (savedCounter) {
            this.taskIdCounter = parseInt(savedCounter) || 0;
        }
        
        // Add initial AI note if no tasks exist
        if (this.tasks.length === 0 && this.aiNotes.length === 0) {
            this.addAINote("Welcome to your Task Hub! I'm Pinky, your AI assistant. I'll help you track tasks and add helpful notes as we work together. 🐙");
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
    new TaskHub();
});