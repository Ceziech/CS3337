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
});