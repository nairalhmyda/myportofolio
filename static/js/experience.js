import {
    createElement,
    debounce,
    requestJson,
    setCollectionState,
} from "./utils.js";
import { showToast } from "./toast.js";

const page = document.getElementById("experience-page");

if (page) {
    const listUrl = page.dataset.listUrl; 
    const loginUrl = page.dataset.loginUrl;
    const permissions = {
        can_star: page.dataset.canStar === "true",
        can_edit: page.dataset.canEdit === "true",
        can_delete: page.dataset.canDelete === "true",
    };

    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search-input");
    const categoryFilter = document.getElementById("experience-category-filter");
    const orderingSelect = document.getElementById("experience-sort");
    const resetButton = document.getElementById("experience-reset-filter");
    const resultsCount = document.getElementById("experience-results-count");
    const grid = document.getElementById("experience-grid");
    const retryButton = document.getElementById("experience-retry-button");
    const addButton = document.getElementById("experience-add-button");
    const modal = document.getElementById("add-experience-modal");
    const form = document.getElementById("experience-form");
    const modalTitle = document.getElementById("add-experience-modal-title");
    const submitButton = document.getElementById("experience-submit-button");

    const states = {
        loading: document.getElementById("experience-loading"),
        error: document.getElementById("experience-error"),
        empty: document.getElementById("experience-empty"),
        grid,
    };

    const endedAtInput = form?.elements.namedItem("ended_at");
    if (endedAtInput) endedAtInput.type = "datetime-local";

    let listController;
    let editingId = null;

    const detailUrl = (id) => `${listUrl}${encodeURIComponent(id)}/`;
    const starUrl = (id) => `${detailUrl(id)}star/`;

    function makeButton(text, className = "button") {
        const button = createElement("button", className, text);
        button.type = "button";
        return button;
    }

    function apiErrorMessage(error) {
        const payload = error.payload;
        if (typeof payload?.detail === "string") return payload.detail;
        if (typeof payload?.message === "string") return payload.message;

        if (payload && typeof payload === "object") {
            const messages = Object.entries(payload).flatMap(([field, issues]) => {
                const entries = Array.isArray(issues) ? issues : [issues];
                return entries.map((issue) => {
                    const text = typeof issue === "string" ? issue : issue?.message;
                    return text ? `${field}: ${text}` : "";
                });
            }).filter(Boolean);
            if (messages.length) return messages.join(" | ");
        }
        return error.message || "Permintaan gagal.";
    }

    function toLocalInput(isoDate) {
        if (!isoDate) return "";
        const date = new Date(isoDate);
        if (Number.isNaN(date.getTime())) return "";
        const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
        return local.toISOString().slice(0, 16);
    }

    function fillForm(experience) {
        if (!form) return;
        form.elements.namedItem("title").value = experience.title ?? "";
        form.elements.namedItem("description").value = experience.description ?? "";
        form.elements.namedItem("category").value = experience.category ?? "full-time";
        form.elements.namedItem("thumbnail").value = experience.thumbnail ?? "";
        form.elements.namedItem("ended_at").value = toLocalInput(experience.ended_at);
    }

    function resetToCreate() {
        editingId = null;
        form?.reset();
        if (modalTitle) modalTitle.textContent = "Tambah Pengalaman Baru";
        if (submitButton) submitButton.textContent = "Tambah Pengalaman";
    }

    async function openEditModal(experienceId, button) {
        button.disabled = true;
        try {
            const current = await requestJson(detailUrl(experienceId));
            editingId = experienceId;
            fillForm(current);
            if (modalTitle) modalTitle.textContent = "Edit Pengalaman";
            if (submitButton) submitButton.textContent = "Simpan Perubahan";
            modal?.showPopover();
        } catch (error) {
            showToast("Gagal membuka edit", apiErrorMessage(error), "error");
        } finally {
            button.disabled = false;
        }
    }

    function formPayload() {
        const data = Object.fromEntries(new FormData(form));
        const endedAt = (data.ended_at || "").trim();
        return {
            title: data.title.trim(),
            description: data.description.trim(),
            category: data.category,
            thumbnail: data.thumbnail.trim() || null,
            ended_at: endedAt ? new Date(endedAt).toISOString() : null,
        };
    }

    function buildExperienceCard(experience) {
        const card = createElement("article", "experience-card");

        if (experience.thumbnail) {
            const image = createElement("img", "project-image");
            image.src = experience.thumbnail;
            image.alt = `Thumbnail ${experience.title}`;
            image.loading = "lazy";
            card.appendChild(image);
        }

        card.appendChild(createElement(
            "span", "experience-category", experience.category_display || experience.category,
        ));
        card.appendChild(createElement("h2", "", experience.title));
        card.appendChild(createElement("p", "experience-description", experience.description));
        card.appendChild(createElement(
            "p", "experience-status",
            experience.is_ongoing ? "Sedang berlangsung" : "Selesai",
        ));

        const actions = createElement("div", "experience-actions");

        if (permissions.can_star) {
            const starButton = makeButton(
                `${experience.is_starred ? "Unstar" : "Star"} (${experience.star_count})`,
                `button button-star${experience.is_starred ? " is-starred" : ""}`,
            );
            starButton.addEventListener("click", async () => {
                starButton.disabled = true;
                try {
                    const updated = await requestJson(starUrl(experience.id), {
                        method: "POST",
                        credentials: "same-origin",
                    });
                    experience.is_starred = updated.is_starred;
                    experience.star_count = updated.star_count;
                    starButton.classList.toggle("is-starred", updated.is_starred);
                    starButton.textContent = `${updated.is_starred ? "Unstar" : "Star"} (${updated.star_count})`;
                } catch (error) {
                    showToast("Star gagal", apiErrorMessage(error), "error");
                } finally {
                    starButton.disabled = false;
                }
            });
            actions.appendChild(starButton);
        } else {
            const login = createElement("a", "button button-secondary", "Login untuk Star");
            login.href = loginUrl;
            actions.appendChild(login);
        }

        if (permissions.can_edit && modal) {
            const editButton = makeButton("Edit", "button button-secondary");
            editButton.addEventListener("click", () => openEditModal(experience.id, editButton));
            actions.appendChild(editButton);
        }

        if (permissions.can_delete) {
            const deleteButton = makeButton("Hapus", "button button-danger");
            deleteButton.addEventListener("click", async () => {
                if (!window.confirm(`Hapus pengalaman “${experience.title}”?`)) return;
                deleteButton.disabled = true;
                try {
                    await requestJson(detailUrl(experience.id), {
                        method: "DELETE", // DRF, bukan POST AJAX lama
                        credentials: "same-origin",
                    });
                    showToast("Berhasil", "Pengalaman berhasil dihapus.", "success");
                    await loadExperiences(searchInput?.value.trim() || "");
                } catch (error) {
                    showToast("Gagal menghapus", apiErrorMessage(error), "error");
                    deleteButton.disabled = false;
                }
            });
            actions.appendChild(deleteButton);
        }

        card.appendChild(actions);
        return card;
    }

    async function loadExperiences(query = "") {
        listController?.abort();
        listController = new AbortController();
        const controller = listController;
        setCollectionState(states, "loading");

        try {
            
            const url = new URL(listUrl, window.location.origin);

            if (query) {
                url.searchParams.set("title", query);
            }

            const category = categoryFilter?.value || "";
            const ordering = orderingSelect?.value || "newest";

            if (category) {
                url.searchParams.set("category", category);
            }

            url.searchParams.set("ordering", ordering);


            const experiences = await requestJson(url, { signal: controller.signal });
            if (!Array.isArray(experiences)) {
                throw new Error("Format API bukan array Experience.");
            }

            if (resultsCount) {
                resultsCount.textContent = "Gagal memuat hasil.";
            }

            grid.replaceChildren();
            if (experiences.length === 0) {
                setCollectionState(states, "empty");
                return;
            }

            const fragment = document.createDocumentFragment();
            experiences.forEach((experience) => {
                fragment.appendChild(buildExperienceCard(experience));
            });
            grid.appendChild(fragment);
            setCollectionState(states, "ready");
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Gagal memuat Experience:", error);
            setCollectionState(states, "error");
        }
    }

    const debouncedSearch = debounce(
        () => loadExperiences(searchInput.value.trim()), 300,
    );
    searchInput?.addEventListener("input", debouncedSearch);
    searchForm?.addEventListener("submit", (event) => {
        event.preventDefault();
        loadExperiences(searchInput?.value.trim() || "");
    });
    retryButton?.addEventListener("click", () => {
        loadExperiences(searchInput?.value.trim() || "");
    });

    addButton?.addEventListener("click", resetToCreate);

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (submitButton) submitButton.disabled = true;
        const isEdit = Boolean(editingId);

        try {
            const payload = formPayload();
            await requestJson(isEdit ? detailUrl(editingId) : listUrl, {
                method: isEdit ? "PATCH" : "POST",
                credentials: "same-origin",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            modal?.hidePopover();
            resetToCreate();
            showToast("Berhasil", isEdit
                ? "Pengalaman berhasil diperbarui."
                : "Pengalaman baru berhasil ditambahkan.", "success");
            await loadExperiences(searchInput?.value.trim() || "");
        } catch (error) {
            showToast("Gagal menyimpan", apiErrorMessage(error), "error");
        } finally {
            if (submitButton) submitButton.disabled = false;
        }
    });

    loadExperiences(searchInput?.value.trim() || "");

        
    categoryFilter?.addEventListener("change", () => {
        loadExperiences(searchInput?.value.trim() || "");
    });

    orderingSelect?.addEventListener("change", () => {
        loadExperiences(searchInput?.value.trim() || "");
    });

    resetButton?.addEventListener("click", () => {
        if (searchInput) searchInput.value = "";
        if (categoryFilter) categoryFilter.value = "";
        if (orderingSelect) orderingSelect.value = "newest";

        loadExperiences("");
    });

}
