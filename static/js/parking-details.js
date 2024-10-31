document.addEventListener("DOMContentLoaded", function() {
    const termsModal = new bootstrap.Modal(document.getElementById("termsModal"));
    termsModal.show();

    const agreeButton = document.getElementById("agreeButton");
    const cancelButton = document.getElementById("cancelButton");

    agreeButton.addEventListener("click", function () {
        termsModal.hide();
    });

    cancelButton.addEventListener("click", function () {
        const cancelUrl = cancelButton.getAttribute("data-url");
        if (cancelUrl) {
            window.location.href = cancelUrl;
        } else {
            console.error("Cancel URL not found.")
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const permit = urlParams.get("permit");

    const permitOptions = document.querySelectorAll(".permit-option");
    permitOptions.forEach(option => {
        const button = option.querySelector(".permit-button");
        const description = option.querySelector(".permit-description");

        if (button.dataset.permit === permit) {
            option.style.display = "block";
            description.style.display = "block";
        } else {
            option.style.display = "none";
        }
    });

    permitOptions.forEach(option => {
        const button = option.querySelector(".permit-button");
        button.addEventListener("click", function () {
            const isSelected = button.classList.contains("selected-button");

            permitOptions.forEach(otherOption => {
                const otherButton = otherOption.querySelector(".permit-button");
                otherButton.classList.remove("selected-button");
                otherOption.querySelector("p").style.display = "block";
                otherOption.style.display = (otherButton.dataset.permit === permit) ? "block" : "none";
                const checkmark = otherButton.querySelector(".checkmark");
                if (checkmark) {
                    checkmark.remove();
                }
            });

            loginButton.style.display = "block";

            if (!isSelected) {
                permitOptions.forEach(otherOption => {
                    if (otherOption !== option) {
                        otherOption.style.display = "none";
                    }
                });
                loginButton.style.display = "none";

                button.classList.add("selected-button");
                option.querySelector("p").style.display = "none";

                if (!button.querySelector(".checkmark")) {
                    const checkmark = document.createElement("span");
                    checkmark.classList.add("checkmark");
                    checkmark.innerHTML = "&#10003;";
                    button.appendChild(checkmark);
                }
            }
        });
    });

    const loginButton = document.querySelector(".login-button");
    loginButton.addEventListener("click", function () {
        const loginUrl = loginButton.getAttribute("data-url");
        if (loginUrl) {
            window.location.href = loginUrl;
        } else {
            console.error("Login URL not found.");
        }
    });
});