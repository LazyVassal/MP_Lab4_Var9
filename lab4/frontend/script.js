// Определяем базовый URL API (локальный или в Docker)
const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
    ? "http://127.0.0.1:8010"
    : "http://backend:8010";

// --- 1. ИНИЦИАЛИЗАЦИЯ И ТЕМА ---
document.addEventListener('DOMContentLoaded', () => {
    // Тема
    const themeToggle = document.getElementById("themeToggle");
    themeToggle.addEventListener("click", () => {
        const isDark = document.documentElement.getAttribute("data-theme") === "dark";
        document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
        themeToggle.textContent = isDark ? "🌙 Тёмная тема" : "☀️ Светлая тема";
    });
});


// --- 2. ПЕРЕКЛЮЧЕНИЕ ВКЛАДОК ---
const tabs = document.querySelectorAll(".tab-btn");
const contents = document.querySelectorAll(".tab-content");

tabs.forEach(btn => {
    btn.addEventListener("click", () => {
        const tabId = btn.dataset.tab;
        tabs.forEach(b => b.classList.remove("active"));
        contents.forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(`${tabId}-tab`).classList.add("active");

        // Загружаем данные для активной вкладки
        if (tabId === "clients") loadClients();
        if (tabId === "memberships") loadActiveMemberships();
        if (tabId === "trainings") loadTrainingsHistory();
    });
});

// --- 3. КЛИЕНТЫ ---
async function loadClients() {
    try {
        const res = await fetch(`${API_BASE}/api/clients`);
        if (!res.ok) throw new Error(`Ошибка ${res.status}`);
        const clients = await res.json();
        renderClients(clients);
    } catch (e) {
        console.error("Не удалось загрузить клиентов:", e);
    }
}

function renderClients(clients) {
    const tbody = document.querySelector("#clientsTable tbody");
    tbody.innerHTML = "";
    clients.forEach(c => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${c.name}</td>
            <td>${c.phone}</td>
            <td>${c.email}</td>
            <td class="action-btns">
                <button class="delete-client" data-id="${c.id}">🗑</button>
                <button class="edit-client" data-id="${c.id}">✏️</button>
                <button class="stat-btn" data-id="${c.id}">📊</button
            </td>
        `;
        tbody.appendChild(row);
    });
}


// --- 4. АБОНЕМЕНТЫ ---
async function loadActiveMemberships() {
    try {
        const res = await fetch(`${API_BASE}/api/memberships/active`);
        if (!res.ok) throw new Error(`Ошибка ${res.status}`);
        const memberships = await res.json();
        renderActiveMemberships(memberships);
    } catch (e) {
        console.error("Не удалось загрузить абонементы:", e);
    }
}

function renderActiveMemberships(memberships) {
    const tbody = document.querySelector("#membershipsTable tbody");
    tbody.innerHTML = "";
    memberships.forEach(m => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${m.client_name}</td>
            <td>${m.type}</td>
            <td>${new Date(m.end_date).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// --- ТРЕНИРОВКИ ---
async function loadTrainingsHistory() {
    try {
        const res = await fetch(`${API_BASE}/api/trainings`);
        if (!res.ok) throw new Error(`Ошибка ${res.status}`);
        const trainings = await res.json();
        renderTrainingsHistory(trainings); // <-- ЗДЕСЬ ВЫЗЫВАЕМ ФУНКЦИЮ
    } catch (e) {
        console.error("Не удалось загрузить тренировки:", e);
    }
}

function renderTrainingsHistory(trainings) {
    const tbody = document.querySelector("#trainingsTable tbody");
    tbody.innerHTML = ""; // Очищаем старые данные

    trainings.forEach(t => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${t.client_id}</td>
            <td>${new Date(t.date).toLocaleDateString()}</td>
            <td>${t.activity}</td>
            <td>${t.duration_minutes}</td>
        `;
        tbody.appendChild(row);
    });
}
// --- 6. НОВЫЕ ФУНКЦИИ: Статистика и Тренировки ---

// Функция для запроса статистики посещений
async function getClientVisitStat(client_id) {
    const res = await fetch(`${API_BASE}/api/clients/${client_id}/visit-stat`);
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Ошибка ${res.status}: ${errorText}`);
    }
    return await res.json();
}

// Функция для запроса истории тренировок
async function getClientTrainings(client_id) {
    const res = await fetch(`${API_BASE}/api/clients/${client_id}/trainings`);
    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Ошибка ${res.status}: ${errorText}`);
    }
    return await res.json();
}


// --- 7. ПОПАП (Модальное окно) ---

// Создаем HTML для модального окна (только один раз)
const modalHTML = `
<div id="myModal" class="modal">
  <div class="modal-content">
    <span class="close-btn">×</span>
    <h2 id="modal-title">Статистика клиента</h2>
    <div id="modal-body">
      <!-- Здесь будут данные -->
    </div>
  </div>
</div>`;

// Добавляем стили для попапа в <head>
const style = document.createElement('style');
style.textContent = `
.modal {
  display: none; /* Скрыт по умолчанию */
  position: fixed; /* Зафиксировать */
  z-index: 1000; /* Поверх всего */
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0,0,0,0.5); /* Полупрозрачный фон */
}
.modal-content {
  background-color: #fefefe;
  margin: 10% auto;
  padding: 20px;
  border-radius: 16px;
  width: 60%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.close-btn {
  color: #aaa;
  float: right;
  font-size: 32px;
  font-weight: bold;
  cursor: pointer;
}
.close-btn:hover {
  color: black;
}
`;
document.head.appendChild(style);
document.body.insertAdjacentHTML('beforeend', modalHTML);

// Функция для показа данных в попапе
function showModal(title, content) {
    document.getElementById('modal-title').innerText = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('myModal').style.display = 'block';
}

// Функция для закрытия попапа
function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

// Обработчик клика на "крестик" закрытия
document.querySelector('.close-btn').addEventListener('click', closeModal);
// Закрытие при клике вне окна контента
document.getElementById('myModal').addEventListener('click', (e) => {
    if (e.target.id === 'myModal') closeModal();
});


// --- 8. ОБРАБОТЧИК СОБЫТИЙ ДЛЯ КНОПКИ СТАТИСТИКИ ---

// Используем Делегирование событий (как мы делали для удаления)
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('stat-btn')) {
        const client_id = event.target.dataset.id;
        
        // Запускаем оба запроса одновременно, чтобы было быстрее
        Promise.all([
            getClientVisitStat(client_id),
            getClientTrainings(client_id)
        ]).then(([statData, trainingsData]) => {
            // Формируем красивый HTML для отображения в модальном окне
            let html = `<p><strong>Всего посещений:</strong> ${statData.total_visits} раз.</p>`;
            html += `<h3>История тренировок:</h3>`;
            
            // Создаем таблицу с историей внутри попапа
            html += `<table style="width:100%; border-collapse: collapse;">
                        <tr style="border-bottom:1px solid #ccc;">
                            <th>Дата</th><th>Активность</th><th>Длительность</th>
                        </tr>`;
            
            trainingsData.forEach(t => {
                html += `<tr style="border-bottom:1px solid #eee;">
                            <td>${new Date(t.date).toLocaleDateString()}</td>
                            <td>${t.activity}</td>
                            <td>${t.duration_minutes} мин.</td>
                        </tr>`;
            });
            html += `</table>`;
            
            showModal(`Статистика для клиента ID ${client_id}`, html);
            
        }).catch(error => {
            console.error("Ошибка при получении статистики:", error);
            alert("Не удалось загрузить данные. Проверьте консоль.");
        });
    }
});