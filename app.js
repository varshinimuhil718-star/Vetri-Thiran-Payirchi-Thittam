document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#plan-form");
    const button = document.querySelector("#generate-btn");

    if (form && button) {
        form.addEventListener("submit", () => {
            button.disabled = true;
            button.style.opacity = "0.7";
            button.querySelector("span").textContent = "Generating your plan...";
        });
    }
});
