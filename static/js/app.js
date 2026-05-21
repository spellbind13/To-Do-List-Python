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

function renderDays(days, offset) {
  if (!dayGrid) {
    return;
  }

  dayGrid.innerHTML = "";

  for (let index = 0; index < offset; index += 1) {
    const spacer = document.createElement("article");
    spacer.className = "day-card day-card-empty";
    spacer.setAttribute("aria-hidden", "true");
    dayGrid.appendChild(spacer);
  }

  days.forEach((day) => {
    const dayCard = document.createElement("article");
    dayCard.className = "day-card";
    const preview = (day.tasks || [])
      .slice(0, 2)
      .map((task) => {
        const stateClass = task.completed ? "day-task-chip day-task-chip-done" : "day-task-chip";
        return `<span class="${stateClass}">${task.title}</span>`;
      })
      .join("");

    const taskLabel = day.count === 1 ? "task" : "tasks";

    dayCard.innerHTML = `
      <span class="day-number">${day.day}</span>
      <strong class="day-count">${day.count} ${taskLabel}</strong>
      <div class="day-task-preview">${preview}</div>
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
      const offset = Number(button.dataset.monthOffset || "0");
      renderDays(days, offset);
    } catch (error) {
      renderDays([], 0);
    }
  });
});

const chartScroll = document.querySelector("#chart-scroll");
const chartLeftButton = document.querySelector("#chart-left");
const chartRightButton = document.querySelector("#chart-right");

if (chartScroll) {
  let isDragging = false;
  let startX = 0;
  let startScrollLeft = 0;

  chartScroll.addEventListener("pointerdown", (event) => {
    isDragging = true;
    startX = event.clientX;
    startScrollLeft = chartScroll.scrollLeft;
    chartScroll.classList.add("is-dragging");
    chartScroll.setPointerCapture(event.pointerId);
  });

  chartScroll.addEventListener("pointermove", (event) => {
    if (!isDragging) {
      return;
    }

    const distance = event.clientX - startX;
    chartScroll.scrollLeft = startScrollLeft - distance;
  });

  function stopDragging(event) {
    if (!isDragging) {
      return;
    }

    isDragging = false;
    chartScroll.classList.remove("is-dragging");

    if (event && typeof event.pointerId === "number") {
      chartScroll.releasePointerCapture(event.pointerId);
    }
  }

  chartScroll.addEventListener("pointerup", stopDragging);
  chartScroll.addEventListener("pointercancel", stopDragging);
  chartScroll.addEventListener("pointerleave", stopDragging);
}

if (chartScroll && chartLeftButton) {
  chartLeftButton.addEventListener("click", () => {
    chartScroll.scrollBy({ left: -260, behavior: "smooth" });
  });
}

if (chartScroll && chartRightButton) {
  chartRightButton.addEventListener("click", () => {
    chartScroll.scrollBy({ left: 260, behavior: "smooth" });
  });
}
