import { tasksApi } from "./api.js";

const form = document.querySelector("#task-form");
const titleInput = document.querySelector("#task-title");
const priorityInput = document.querySelector("#task-priority");
const deadlineInput = document.querySelector("#task-deadline");
const list = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const fabBtn = document.querySelector("#fab-add");
const modal = document.querySelector("#task-modal");
const closeModalBtn = document.querySelector("#close-modal");
const clearCompletedBtn = document.querySelector("#clear-completed");
const filterBtns = document.querySelectorAll(".filter-btn");

let currentSortField = "created_at";
let currentSortOrder = "desc";
let currentFilter = "all";

function formatDate(isoString) {
    if (!isoString) return "—";
    const date = new Date(isoString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}
function toDatetimeLocal(isoString) {
    if (!isoString) return "";
    const date = new Date(isoString);
    const pad = (num) => String(num).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function openModal() { modal.classList.remove("hidden"); titleInput.focus(); }
function closeModal() { modal.classList.add("hidden"); form.reset(); }
fabBtn.addEventListener("click", openModal);
closeModalBtn.addEventListener("click", closeModal);
modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        filterBtns.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        currentFilter = btn.dataset.filter;
        loadTasks();
    });
});

clearCompletedBtn.addEventListener("click", async () => {
    try {
        await tasksApi.clearCompleted();
        loadTasks();
    } catch (err) {
        alert(err.message);
    }
});

document.querySelectorAll(".sortable").forEach(header => {
    header.addEventListener("click", () => {
        const field = header.dataset.sort;

        if (currentSortField === field) {
            currentSortOrder = currentSortOrder === "asc" ? "desc" : "asc";
        } else {
            currentSortField = field;
            currentSortOrder = "asc";
        }

        document.querySelectorAll(".sortable").forEach(h => {
            const icon = h.querySelector(".sort-icon");
            if (h.dataset.sort === currentSortField) {
                icon.textContent = currentSortOrder === "asc" ? "↑" : "↓";
                icon.classList.add("active");
            } else {
                icon.textContent = "↕";
                icon.classList.remove("active");
            }
        });

        loadTasks();
    });
});

function createTaskRow(task) {
    const row = document.createElement("div");
    row.className = "task-item";
    if (task.is_completed) row.classList.add("completed");

    // Статус
    const statusCell = document.createElement("div");
    statusCell.className = "col-check";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.is_completed;

    checkbox.addEventListener("change", async () => {
        try {
            const updatedTask = await tasksApi.toggle(task.id);

            if (updatedTask.is_completed) {
                row.classList.add("completed");
            } else {
                row.classList.remove("completed");
            }
            if (currentFilter !== "all") {
                row.style.display = "none";
                setTimeout(loadTasks, 300);
            }

        } catch (err) {
            checkbox.checked = !checkbox.checked;
            alert(err.message);
        }
    });
    statusCell.appendChild(checkbox);

    // Название
    const titleCell = document.createElement("div");
    titleCell.className = "col-title";
    const titleSpan = document.createElement("span");
    titleSpan.className = "title-text";
    titleSpan.textContent = task.title;
    titleCell.appendChild(titleSpan);

    // Приоритет
    const priorityCell = document.createElement("div");
    priorityCell.className = "col-priority";
    const badge = document.createElement("span");
    badge.className = `badge badge-${task.priority.toLowerCase()}`;
    badge.textContent = task.priority;
    priorityCell.appendChild(badge);

    // Дата создания
    const createdCell = document.createElement("div");
    createdCell.className = "col-date";
    createdCell.innerHTML = `<span class="date-text">${formatDate(task.created_at)}</span>`;

    // Дедлайн
    const deadlineCell = document.createElement("div");
    deadlineCell.className = "col-date";
    const dlSpan = document.createElement("span");

    if (task.deadline) {
        dlSpan.className = `date-text ${task.is_completed ? '' : 'deadline-text active'}`;
        dlSpan.textContent = formatDate(task.deadline);
    } else {
        // Добавляем класс deadline-empty, чтобы не зачеркивать прочерк
        dlSpan.className = `date-text deadline-empty`;
        dlSpan.textContent = "—";
    }
    deadlineCell.appendChild(dlSpan);

    // Кнопки
    const actionsCell = document.createElement("div");
    actionsCell.className = "col-actions";

    const editBtn = document.createElement("button");
    editBtn.className = "btn-icon";
    editBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>`;
    editBtn.addEventListener("click", () => enterEditMode(row, task));

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "btn-icon delete";
    deleteBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`;

    deleteBtn.addEventListener("click", async () => {
        try {
            await tasksApi.remove(task.id);
            await loadTasks();
        } catch (err) {
            alert(err.message);
        }
    });

    actionsCell.appendChild(editBtn);
    actionsCell.appendChild(deleteBtn);

    row.appendChild(statusCell);
    row.appendChild(titleCell);
    row.appendChild(priorityCell);
    row.appendChild(createdCell);
    row.appendChild(deadlineCell);
    row.appendChild(actionsCell);

    return row;
}

function enterEditMode(row, task) {
    row.innerHTML = "";
    row.classList.remove("completed");

    const editForm = document.createElement("div");
    editForm.className = "inline-edit-form";

    const statusCell = document.createElement("div");

    const titleCell = document.createElement("div");
    titleCell.className = "col-title";
    const titleInp = document.createElement("input");
    titleInp.type = "text";
    titleInp.className = "inline-edit-input";
    titleInp.value = task.title;
    titleCell.appendChild(titleInp);

    const priorityCell = document.createElement("div");
    priorityCell.className = "col-priority";
    const prioInp = document.createElement("select");
    prioInp.className = "inline-edit-input";
    ["Низкий", "Средний", "Высокий"].forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.textContent = p;
        if (p === task.priority) opt.selected = true;
        prioInp.appendChild(opt);
    });
    priorityCell.appendChild(prioInp);

    const createdCell = document.createElement("div");
    createdCell.className = "col-date";
    createdCell.innerHTML = `<span class="date-text">${formatDate(task.created_at)}</span>`;

    const deadlineCell = document.createElement("div");
    deadlineCell.className = "col-date";
    const deadInp = document.createElement("input");
    deadInp.type = "datetime-local";
    deadInp.className = "inline-edit-input";
    deadInp.value = toDatetimeLocal(task.deadline);
    deadlineCell.appendChild(deadInp);

    const actionsCell = document.createElement("div");
    actionsCell.className = "col-actions";
    actionsCell.style.opacity = "1";

    const saveBtn = document.createElement("button");
    saveBtn.className = "btn-icon save";
    saveBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

    const cancelBtn = document.createElement("button");
    cancelBtn.className = "btn-icon cancel";
    cancelBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`;

    saveBtn.addEventListener("click", async () => {
        try {
            const changes = {
                title: titleInp.value.trim(),
                priority: prioInp.value,
                deadline: deadInp.value ? deadInp.value : null
            };
            if (!changes.title) throw new Error("Название не может быть пустым");
            await tasksApi.update(task.id, changes);
            await loadTasks();
        } catch (err) { alert(err.message); }
    });

    cancelBtn.addEventListener("click", () => loadTasks());

    actionsCell.appendChild(saveBtn);
    actionsCell.appendChild(cancelBtn);

    editForm.appendChild(statusCell);
    editForm.appendChild(titleCell);
    editForm.appendChild(priorityCell);
    editForm.appendChild(createdCell);
    editForm.appendChild(deadlineCell);
    editForm.appendChild(actionsCell);
    row.appendChild(editForm);
}

async function loadTasks() {
    list.style.opacity = "0.5";
    const sortQuery = currentSortOrder === "asc" ? currentSortField : `-${currentSortField}`;

    try {
        const tasks = await tasksApi.getAll(currentFilter, sortQuery);

        if (taskCount.textContent !== String(tasks.length)) {
            taskCount.textContent = tasks.length;
        }

        list.innerHTML = "";
        tasks.forEach(task => {
            list.appendChild(createTaskRow(task));
        });
    } catch (error) {
        alert(error.message);
    } finally {
        list.style.opacity = "1";
    }
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const title = titleInput.value.trim();
    const priority = priorityInput.value;
    const deadline = deadlineInput.value ? deadlineInput.value : null;

    try {
        await tasksApi.create({ title, priority, deadline });
        closeModal();
        loadTasks();
    } catch (error) {
        alert(error.message);
    }
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".sortable").forEach(h => {
        if (h.dataset.sort === currentSortField) {
            h.querySelector(".sort-icon").textContent = "↓";
            h.querySelector(".sort-icon").classList.add("active");
        }
    });
    loadTasks();
});