const cards = document.querySelectorAll("[data-task-card]");

cards.forEach((card, index) => {
  card.style.animationDelay = `${index * 70}ms`;
});

const form = document.querySelector(".task-form");
const input = document.querySelector("#title");

if (form && input) {
  form.addEventListener("submit", (event) => {
    const value = input.value.trim();

    if (!value) {
      event.preventDefault();
      input.focus();
      return;
    }

    form.classList.add("is-submitting");
  });
}
