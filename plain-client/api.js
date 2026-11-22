const CONFIG = {
    API_BASE_URL: "",
    MAX_RETRIES: 3,
    BASE_DELAY_MS: 300
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchWithRetry(url, options) {
    const method = (options.method || "GET").toUpperCase();

    const isIdempotent = ["GET", "PUT", "DELETE"].includes(method);

    let attempt = 0;

    while (attempt < CONFIG.MAX_RETRIES) {
        try {
            const response = await fetch(url, options);

            if (!response.ok && response.status >= 500 && isIdempotent) {
                throw new Error(`Server error: ${response.status}`);
            }

            return response;

        } catch (error) {
            if (!isIdempotent || attempt >= CONFIG.MAX_RETRIES - 1) {
                throw error;
            }

            const delay = (CONFIG.BASE_DELAY_MS * Math.pow(2, attempt)) + (Math.random() * 100);
            console.warn(`[Retry] Сетевая ошибка (${method}). Попытка ${attempt + 1} через ${Math.round(delay)}мс...`);

            await sleep(delay);
            attempt++;
        }
    }
}


async function request(path, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${path}`;

    const headers = {
        "Accept": "application/json",
        ...options.headers
    };

    if (options.body) {
        headers["Content-Type"] = "application/json";
    }

    const fetchOptions = { ...options, headers };

    try {
        const response = await fetchWithRetry(url, fetchOptions);

        if (response.status === 204) return null;

        const data = await response.json().catch(() => null);

        if (!response.ok) {
            const errorDetail = data?.detail;
            if (Array.isArray(errorDetail)) {
                throw new Error(errorDetail[0]?.msg || "Ошибка валидации данных");
            }
            throw new Error(errorDetail || `Ошибка HTTP ${response.status}`);
        }

        return data;
    } catch (error) {
        if (error.name === 'TypeError' || error.message.includes('Failed to fetch')) {
            throw new Error("Сервер недоступен. Проверьте подключение.");
        }
        throw error;
    }
}

export const tasksApi = {
    getAll: (filter = "all", sort = "-created_at") =>
        request(`/api/tasks?filter=${filter}&sort=${sort}`),

    create: (task) => request("/api/tasks", {
        method: "POST",
        body: JSON.stringify(task)
    }),

    update: (id, changes) => request(`/api/tasks/${id}`, {
        method: "PATCH",
        body: JSON.stringify(changes)
    }),

    toggle: (id) => request(`/api/tasks/${id}/toggle`, {
        method: "POST"
    }),

    remove: (id) => request(`/api/tasks/${id}`, {
        method: "DELETE"
    }),

    clearCompleted: () => request("/api/tasks", {
        method: "DELETE"
    })
};