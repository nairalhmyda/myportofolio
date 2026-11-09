import {
    createElement,
    debounce,
    formErrorMessage,
    requestJson,
    setCollectionState,
} from "./utils.js";
import { showToast } from "./toast.js";

const page = document.getElementById("projects-page");

if (page) {
    const listUrl = page.dataset.listUrl;
    const createUrl = page.dataset.createUrl;
    const loginUrl = page.dataset.loginUrl;

    const searchForm = document.getElementById("project-search-form");
    const searchInput = document.getElementById("project-search-input");
    const projectForm = document.getElementById("project-form");
    const grid = document.getElementById("project-grid");

    const states = {
        loading: document.getElementById("project-loading"),
        error: document.getElementById("project-error"),
        empty: document.getElementById("project-empty"),
        grid,
    };

    let listController;

    function actionButton(label, className = "button") {
        const button = createElement("button", className, label);
        button.type = "button";
        return button;
    }

    function buildProjectCard(project, permissions) {
        const card = createElement("article", "experience-card");

        if (project.project_image_url) {
            const image = createElement("img", "project-image");
            image.src = project.project_image_url;
            image.alt = `Gambar ${project.title}`;
            image.loading = "lazy";
            card.appendChild(image);
        }

        card.appendChild(createElement("span", "experience-category", String(project.year)));
        card.appendChild(createElement("h2", "", project.title));
        card.appendChild(createElement("p", "experience-description", project.description));
        card.appendChild(createElement("p", "experience-status", project.tech_stack));

        const actions = createElement("div", "project-actions");

        if (project.github_url) {
            const githubLink = createElement("a", "button", "View on GitHub");
            githubLink.href = project.github_url;
            githubLink.target = "_blank";
            githubLink.rel = "noopener noreferrer";
            actions.appendChild(githubLink);
        }

        if (permissions.can_star) {
            const starButton = actionButton(
                `${project.is_starred ? "Unstar" : "Star"} (${project.star_count})`,
                `button button-star${project.is_starred ? " is-starred" : ""}`,
            );
            starButton.title = project.starred_by_names.length
                ? `Dibintangi oleh ${project.starred_by_names.join(", ")}`
                : "Jadilah yang pertama memberi star";

            starButton.addEventListener("click", async () => {
                starButton.disabled = true;
                try {
                    const result = await requestJson(project.urls.star, { method: "POST" });
                    project.is_starred = result.is_starred;
                    project.star_count = result.star_count;
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
            editLink.href = project.urls.edit;
            actions.appendChild(editLink);
        }

        if (permissions.can_delete) {
            const deleteButton = actionButton("Hapus", "button button-danger");
            deleteButton.addEventListener("click", async () => {
                if (!window.confirm(`Hapus project “${project.title}”?`)) return;

                deleteButton.disabled = true;
                try {
                    await requestJson(project.urls.delete, { method: "POST" });
                    showToast("Berhasil", "Proyek berhasil dihapus.", "success");
                    await loadProjects(searchInput.value.trim());
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

    async function loadProjects(query = "") {
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
            data.items.forEach((project) => {
                fragment.appendChild(buildProjectCard(project, data.permissions));
            });
            grid.appendChild(fragment);
            setCollectionState(states, "ready");
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Gagal memuat projects:", error);
            setCollectionState(states, "error");
        }
    }

    const debouncedSearch = debounce(() => loadProjects(searchInput.value.trim()), 300);

    searchInput?.addEventListener("input", debouncedSearch);
    searchForm?.addEventListener("submit", (event) => {
        event.preventDefault();
        loadProjects(searchInput.value.trim());
    });

    projectForm?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitButton = projectForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            await requestJson(createUrl, {
                method: "POST",
                body: new FormData(projectForm),
            });
            projectForm.reset();
            document.getElementById("add-project-modal")?.hidePopover();
            showToast("Berhasil", "Proyek baru berhasil ditambahkan.", "success");
            await loadProjects(searchInput.value.trim());
        } catch (error) {
            showToast(
                "Gagal menambahkan proyek",
                formErrorMessage(error.payload, error.message),
                "error",
            );
        } finally {
            submitButton.disabled = false;
        }
    });

    loadProjects(searchInput?.value.trim() || "");
}
