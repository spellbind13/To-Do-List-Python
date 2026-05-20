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

const monthButtons = document.querySelectorAll("[data-month-button]");
const dayPanelTitle = document.querySelector("#day-panel-title");
const dayGrid = document.querySelector("#day-grid");

function renderDays(days) {
  if (!dayGrid) {
    return;
  }

  dayGrid.innerHTML = "";

  days.forEach((day) => {
    const dayCard = document.createElement("article");
    dayCard.className = "day-card";
    dayCard.innerHTML = `
      <span class="day-number">${day.day}</span>
      <strong class="day-count">${day.count}</strong>
    `;
    dayGrid.appendChild(dayCard);
  });
}

monthButtons.forEach((button, index) => {
  if (index === 0) {
    button.classList.add("is-selected");
  }

  button.addEventListener("click", () => {
    monthButtons.forEach((item) => item.classList.remove("is-selected"));
    button.classList.add("is-selected");

    if (dayPanelTitle) {
      dayPanelTitle.textContent = button.dataset.monthLabel || "Selected month";
    }

    try {
      const days = JSON.parse(button.dataset.monthDays || "[]");
      renderDays(days);
    } catch (error) {
      renderDays([]);
    }
  });
});
