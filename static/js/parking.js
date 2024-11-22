document.addEventListener("DOMContentLoaded", function () {
    const cards = document.querySelectorAll(".card[data-url]");

    cards.forEach(card => {
        card.addEventListener("click", function () {
            const url = card.getAttribute("data-url");
            if (url) {
                window.location.href = url;
            } else {
                console.error("URL not found for card:", card);
            }
        });
    });
});