const API_BASE = window.__API_BASE__ || "/api";

const inputEl  = document.getElementById("input");
const outputEl = document.getElementById("output");
const statusEl = document.getElementById("status");
const fileEl   = document.getElementById("file");
const btn      = document.getElementById("convert");
const tabs     = document.querySelectorAll(".tab");

const navBtn = document.getElementById("nav-btn");
const pageSubtitle = document.getElementById("page-subtitle");
const converterPage = document.getElementById("converter-page");
const statsPage = document.getElementById("stats-page");

let mode = "encode";
let isStatsPage = false;

// Универсальная функция для fetch с таймаутом
async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 1000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(resource, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    if (error.name === 'AbortError') {
      throw new Error("TIMEOUT");
    }
    throw error;
  }
}

tabs.forEach(t => t.addEventListener("click", () => {
  tabs.forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  mode = t.dataset.mode;
  outputEl.value = "";
  setStatus("");
}));

navBtn.addEventListener("click", () => {
  isStatsPage = !isStatsPage;
  setStatus("");

  if (isStatsPage) {
    converterPage.style.display = "none";
    statsPage.style.display = "block";
    navBtn.textContent = "← Назад";
    pageSubtitle.textContent = "Детальная информация о работе сервиса";
    loadStats();
  } else {
    converterPage.style.display = "block";
    statsPage.style.display = "none";
    navBtn.textContent = "📊 Статистика";
    pageSubtitle.textContent = "Кодирование и декодирование текста";
  }
});

// --- ОСНОВНОЙ ПЕРЕВОД (Тоже добавим защиту на случай выключения бэкенда) ---
btn.addEventListener("click", async () => {
  const text = inputEl.value.trim();
  if (!text) return setStatus("Введите текст", "error");

  setStatus("Перевод...", "ok");
  try {
    const url = `${API_BASE}/${mode}`;
    const body = mode === "encode" ? { text } : { morse: text };

    // Используем таймаут и для перевода
    const res = await fetchWithTimeout(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      timeout: 1500
    });

    if (res.status === 502 || res.status === 503) {
       throw new Error("SERVER_DOWN");
    }

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    outputEl.value = mode === "encode" ? data.morse : data.text;
    setStatus("Готово", "ok");
  } catch (e) {
    if (e.message === "SERVER_DOWN" || e.message === "TIMEOUT") {
       alert("⚠️ Ошибка! Основной микросервис перевода (morse-backend) отключен или не отвечает.");
       setStatus("Сервис перевода недоступен", "error");
    } else {
       setStatus("Ошибка: " + e.message, "error");
    }
  }
});

// --- СЕРВИС ЗАГРУЗКИ ФАЙЛА (Добавили проверку) ---
fileEl.addEventListener("change", async () => {
  const file = fileEl.files[0];
  if (!file) return;

  const fd = new FormData();
  fd.append("file", file);

  setStatus("Обработка файла...", "ok");

  try {
    // Используем fetchWithTimeout, чтобы не ждать 10 секунд, если бэкенд выключен
    const res = await fetchWithTimeout(`${API_BASE}/encode-file`, {
      method: "POST",
      body: fd,
      timeout: 2000 // 2 секунды на загрузку и обработку файла
    });

    // Проверяем, не отключен ли сервис
    if (res.status === 502 || res.status === 503) {
      throw new Error("SERVER_DOWN");
    }

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    inputEl.value = data.original;
    outputEl.value = data.morse;
    setStatus(`Файл "${file.name}" обработан`, "ok");
  } catch (e) {
    // Если ошибка из-за выключенного сервиса или таймаута — показываем алерт
    if (e.message === "SERVER_DOWN" || e.message === "TIMEOUT") {
       alert("⚠️ Ошибка! Микросервис перевода (morse-backend) отключен. Загрузка файлов невозможна.");
       setStatus("Сервис недоступен", "error");
    } else {
       setStatus("Ошибка: " + e.message, "error");
    }

    // Очищаем поле выбора файла, чтобы можно было попробовать снова
    fileEl.value = "";
  }
});

function setStatus(msg, cls = "") {
  statusEl.textContent = msg;
  statusEl.className = "status " + cls;
}

// --- Статистика ---
async function loadStats() {
  const statTotal = document.getElementById("stat-total");
  const statEnc = document.getElementById("stat-enc");
  const statDec = document.getElementById("stat-dec");

  statTotal.textContent = "Загрузка...";
  statEnc.textContent = "...";
  statDec.textContent = "...";

  try {
    const res = await fetchWithTimeout("/stats/stats", { timeout: 1000 });

    if (res.status === 502 || res.status === 503) {
      throw new Error("SERVER_DOWN");
    }

    if (res.ok) {
      const data = await res.json();
      statTotal.textContent = data.total;
      statEnc.textContent = data.encodes;
      statDec.textContent = data.decodes;
    }
  } catch (e) {
    alert("⚠️ Ошибка! Микросервис статистики (stats-service) отключен или не отвечает.");
    statTotal.innerHTML = '<span style="color: #f87171; font-size: 14px;">Сервис отключен</span>';
    statEnc.textContent = "-";
    statDec.textContent = "-";
  }
}

// --- Экспорт файлов ---
async function downloadFile(format) {
  const morseText = outputEl.value.trim();
  const originalText = inputEl.value.trim();

  if (!morseText) return setStatus("Сначала сделайте перевод", "error");

  setStatus("Генерация файла...", "ok");
  try {
    const res = await fetchWithTimeout(`/export/export/${format}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original: originalText, morse: morseText }),
      timeout: 1500
    });

    if (res.status === 502 || res.status === 503) {
      throw new Error("SERVER_DOWN");
    }

    if (!res.ok) throw new Error("Ошибка экспорта");

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `morse_result.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setStatus(`Файл .${format} скачан`, "ok");
  } catch (e) {
    alert(`⚠️ Ошибка! Микросервис экспорта (export-service) отключен или не отвечает.`);
    setStatus("Сервис экспорта недоступен", "error");
  }
}

document.getElementById("export-txt").addEventListener("click", () => downloadFile("txt"));
document.getElementById("export-csv").addEventListener("click", () => downloadFile("csv"));
document.getElementById("export-pdf").addEventListener("click", () => downloadFile("pdf"));