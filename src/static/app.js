document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper to escape HTML to prevent XSS when inserting user-provided strings
  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, (m) => map[m]);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants list markup (with fallback)
        const participantsItems = details.participants.length
          ? details.participants.map((p) => `<li><span class="participant-name">${escapeHtml(p)}</span><button class="delete-btn" data-activity="${escapeHtml(name)}" data-email="${escapeHtml(p)}" title="Unregister">✕</button></li>`).join("")
          : `<li class="no-participants">No participants yet</li>`;

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>

          <div class="participants-section">
            <h5>Participants</h5>
            <ul class="participants-list">
              ${participantsItems}
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button event listeners
        if (details.participants.length) {
          activityCard.querySelectorAll(".delete-btn").forEach((btn) => {
            btn.addEventListener("click", async (event) => {
              event.stopPropagation();
              const activity = btn.getAttribute("data-activity");
              const email = btn.getAttribute("data-email");

              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
                  {
                    method: "POST",
                  }
                );

                const result = await response.json();

                if (response.ok) {
                  messageDiv.textContent = result.message;
                  messageDiv.className = "success";
                  fetchActivities(); // Refresh the activities list
                } else {
                  messageDiv.textContent = result.detail || "An error occurred";
                  messageDiv.className = "error";
                }

                messageDiv.classList.remove("hidden");

                // Hide message after 5 seconds
                setTimeout(() => {
                  messageDiv.classList.add("hidden");
                }, 5000);
              } catch (error) {
                messageDiv.textContent = "Failed to unregister. Please try again.";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
                console.error("Error unregistering:", error);
              }
            });
          });
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh the activities list to show the new participant
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
