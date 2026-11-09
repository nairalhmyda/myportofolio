let toastTimer;

export function showToast(title, message, type = "normal", duration = 3000) {
    const toast = document.getElementById("toast-component");
    const toastTitle = document.getElementById("toast-title");
    const toastMessage = document.getElementById("toast-message");

    if (!toast || !toastTitle || !toastMessage) return;

    toast.classList.remove("toast-success", "toast-error", "toast-normal");
    toast.classList.add(`toast-${type}`);
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    clearTimeout(toastTimer);

    if (typeof toast.showPopover === "function" && !toast.matches(":popover-open")) {
        toast.showPopover();
    }

    toast.classList.remove("toast-hidden");
    toast.classList.add("toast-show");

    toastTimer = setTimeout(() => {
        toast.classList.remove("toast-show");
        toast.classList.add("toast-hidden");

        toastTimer = setTimeout(() => {
            if (typeof toast.hidePopover === "function" && toast.matches(":popover-open")) {
                toast.hidePopover();
            }
        }, 300);
    }, duration);
}
