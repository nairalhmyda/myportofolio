export function getCookie(name) {
    const cookie = document.cookie
        .split(";")
        .map((item) => item.trim())
        .find((item) => item.startsWith(`${name}=`));

    return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
}

export async function requestJson(url, options = {}) {
    const config = { ...options };
    const headers = new Headers(config.headers || {});
    headers.set("Accept", "application/json");
    headers.set("X-Requested-With", "XMLHttpRequest");

    const method = (config.method || "GET").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        const csrfToken = getCookie("csrftoken");
        if (csrfToken) headers.set("X-CSRFToken", csrfToken);
    }

    config.headers = headers;
    const response = await fetch(url, config);
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
        const error = new Error(payload.message || `Request gagal (${response.status}).`);
        error.status = response.status;
        error.payload = payload;
        throw error;
    }

    return payload;
}

export function debounce(callback, delay = 300) {
    let timerId;
    return (...args) => {
        clearTimeout(timerId);
        timerId = setTimeout(() => callback(...args), delay);
    };
}

export function formErrorMessage(payload, fallback = "Data belum dapat disimpan.") {
    if (!payload?.errors) return payload?.message || fallback;

    const messages = Object.values(payload.errors)
        .flat()
        .map((error) => error.message)
        .filter(Boolean);

    return messages.length ? messages.join(" ") : fallback;
}

export function setCollectionState(elements, state) {
    const { loading, error, empty, grid } = elements;
    loading?.classList.toggle("hide", state !== "loading");
    error?.classList.toggle("hide", state !== "error");
    empty?.classList.toggle("hide", state !== "empty");
    grid?.classList.toggle("hide", state !== "ready");
}

export function createElement(tagName, className, text) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}
