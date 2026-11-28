// AJAX star ratings: send the rating form with fetch() and update the page without reloading.
// Elements are found through data attributes , and text is set with textContent.

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-rating-form]");
  if (!form) {
    return; // visitors who are not logged in have no rating form
  }

  const average = document.querySelector("[data-rating-average]");
  const count = document.querySelector("[data-rating-count]");
  const status = form.querySelector("[data-rating-status]");
  const button = form.querySelector('button[type="submit"]');

  form.addEventListener("submit", async (event) => {
    event.preventDefault(); // stop the normal page reload: we send the form ourselves

    button.disabled = true;
    status.textContent = "";

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form), // includes the CSRF token from {% csrf_token %}
      });
      const data = await response.json();

      if (response.ok) {
        average.textContent = data.average;
        count.textContent = data.count_label;
        status.textContent = data.message;
      } else {
        status.textContent = data.error;
      }
      status.classList.toggle("text-success", response.ok);
      status.classList.toggle("text-danger", !response.ok);
    } catch (error) {
      status.textContent = form.getAttribute("data-network-error");
      status.classList.add("text-danger");
    } finally {
      button.disabled = false;
    }
  });
});