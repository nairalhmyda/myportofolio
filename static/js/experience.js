import {
    createElement,
    debounce,
    formErrorMessage,
    requestJson,
    setCollectionState,
} from "./utils.js";
import { showToast } from "./toast.js";

const page = document.getElementById("experience-page");

if (page) {
    const listUrl = page.dataset.listUrl;
    const createUrl = page.dataset.createUrl;
    const loginUrl = page.dataset.loginUrl;

    const searchForm = document.getElementById("experience-search-form");
    const searchInput = document.getElementById("experience-search-input");
    const experienceForm = document.getElementById("experience-form");
    const retryButton = document.getElementById("experience-retry-button");
    const grid = document.getElementById("experience-grid");

    const states = {
        loading: document.getElementById("experience-loading"),
        error: document.getElementById("experience-error"),
        empty: document.getElementById("experience-empty"),
        grid,
    };

    let listController;

    function buildExperienceCard(experience, permissions) {
        const card = createElement("article", "experience-card");

        if (experience.thumbnail) {
            const image = createElement("img", "project-image");
            image.src = experience.thumbnail;
            image.alt = `Thumbnail ${experience.title}`;
            image.loading = "lazy";
            card.appendChild(image);
        }

        card.appendChild(createElement("span", "experience-category", experience.category_display));
        card.appendChild(createElement("h2", "", experience.title));
        card.appendChild(createElement("p", "experience-description", experience.description));
        card.appendChild(
            createElement(
                "p",
                "experience-status",
                experience.is_ongoing ? "Sedang berlangsung" : "Selesai",
            ),
        );

        const actions = createElement("div", "experience-actions");

        if (permissions.can_star) {
            const starButton = createElement(
                "button",
                `button button-star${experience.is_starred ? " is-starred" : ""}`,
                `${experience.is_starred ? "Unstar" : "Star"} (${experience.star_count})`,
            );
            starButton.type = "button";

            starButton.addEventListener("click", async () => {
                starButton.disabled = true;
                try {
                    const result = await requestJson(experience.urls.star, { method: "POST" });
                    experience.is_starred = result.is_starred;
                    experience.star_count = result.star_count;
                    starButton.classList.toggle("is-starred", result.is_starred);
                    starButton.textContent = `${result.is_starred ? "Unstar" : "Star"} (${result.star_count})`;
                } catch (error) {
                    showToast("Star gagal", error.message, "error");
                } finally {
                    starButton.disabled = false;
                }
            });
            actions.appendChild(starButton);
        } else {
            const loginLink = createElement("a", "button button-secondary", "Login untuk Star");
            loginLink.href = loginUrl;
            actions.appendChild(loginLink);
        }

        if (permissions.can_edit) {
            const editLink = createElement("a", "button button-secondary", "Edit");
            editLink.href = experience.urls.edit;
            actions.appendChild(editLink);
        }

        if (permissions.can_delete) {
            const deleteButton = createElement("button", "button button-danger", "Hapus");
            deleteButton.type = "button";
            deleteButton.addEventListener("click", async () => {
                if (!window.confirm(`Hapus pengalaman “${experience.title}”?`)) return;

                deleteButton.disabled = true;
                try {
                    await requestJson(experience.urls.delete, { method: "POST" });
                    showToast("Berhasil", "Pengalaman berhasil dihapus.", "success");
                    await loadExperiences(searchInput.value.trim());
                } catch (error) {
                    deleteButton.disabled = false;
                    showToast("Gagal menghapus", error.message, "error");
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
        setCollectionState(states, "loading");

        try {
            const url = new URL(listUrl, window.location.origin);
            if (query) url.searchParams.set("title", query);

            const data = await requestJson(url, { signal: listController.signal });
            grid.replaceChildren();

            if (!data.items.length) {
                setCollectionState(states, "empty");
                return;
            }

            const fragment = document.createDocumentFragment();
            data.items.forEach((experience) => {
                fragment.appendChild(buildExperienceCard(experience, data.permissions));
            });
            grid.appendChild(fragment);
            setCollectionState(states, "ready");
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Gagal memuat experience:", error);
            setCollectionState(states, "error");
        }
    }

    const debouncedSearch = debounce(() => loadExperiences(searchInput.value.trim()), 300);

    searchInput?.addEventListener("input", debouncedSearch);
    retryButton?.addEventListener("click", () => {
        loadExperiences(searchInput?.value.trim() || "");
    });
    searchForm?.addEventListener("submit", (event) => {
        event.preventDefault();
        loadExperiences(searchInput.value.trim());
    });

    experienceForm?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitButton = experienceForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            await requestJson(createUrl, {
                method: "POST",
                body: new FormData(experienceForm),
            });
            experienceForm.reset();
            document.getElementById("add-experience-modal")?.hidePopover();
            showToast("Berhasil", "Pengalaman baru berhasil ditambahkan.", "success");
            await loadExperiences(searchInput.value.trim());
        } catch (error) {
            showToast(
                "Gagal menambahkan pengalaman",
                formErrorMessage(error.payload, error.message),
                "error",
            );
        } finally {
            submitButton.disabled = false;
        }
    });

    loadExperiences(searchInput?.value.trim() || "");
}
