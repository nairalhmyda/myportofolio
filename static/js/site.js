const menuToggle = document.getElementById("menu-toggle");
const siteMenu = document.getElementById("site-menu");

if (menuToggle && siteMenu) {
    const menuLabel = menuToggle.querySelector(".menu-label");
    const menuIcon = menuToggle.querySelector(".menu-icon");

    menuToggle.addEventListener("click", () => {
        const isOpen = siteMenu.classList.toggle("is-open");
        menuToggle.setAttribute("aria-expanded", String(isOpen));

        if (menuLabel) menuLabel.textContent = isOpen ? "CLOSE" : "MENU";
        if (menuIcon) menuIcon.textContent = isOpen ? "×" : "+";
    });
}
