// dashboard.js - Handles the internship application tracker
// Full CRUD operations with the backend tracker API

document.addEventListener("DOMContentLoaded", () => {

  const addAppBtn    = document.getElementById("addAppBtn");
  const modalOverlay = document.getElementById("modalOverlay");
  const closeModal   = document.getElementById("closeModal");
  const cancelBtn    = document.getElementById("cancelBtn");
  const saveAppBtn   = document.getElementById("saveAppBtn");
  const trackerTable = document.getElementById("trackerTable");
  const trackerBody  = document.getElementById("trackerBody");
  const emptyState   = document.getElementById("emptyState");

  const userId = InternMitra.getUserId();

  // ── Load applications on page load ────────────────────────────────────────
  loadApplications();
  loadStats();

  // ── Modal Controls ─────────────────────────────────────────────────────────
  addAppBtn.addEventListener("click", () => {
    clearForm();
    modalOverlay.classList.add("active");
  });

  closeModal.addEventListener("click", () => modalOverlay.classList.remove("active"));
  cancelBtn.addEventListener("click", () => modalOverlay.classList.remove("active"));

  // Close modal on overlay click
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) modalOverlay.classList.remove("active");
  });

  // ── Save Application ───────────────────────────────────────────────────────
  saveAppBtn.addEventListener("click", async () => {
    const company = document.getElementById("companyInput").value.trim();
    const role    = document.getElementById("roleInput").value.trim();

    if (!company || !role) {
      InternMitra.showToast("Company and Role are required.", "error");
      return;
    }

    saveAppBtn.textContent = "Saving...";
    saveAppBtn.disabled = true;

    try {
      await InternMitra.apiCall("/tracker/add", "POST", {
        user_id: userId,
        company: company,
        role: role,
        status: document.getElementById("statusInput").value,
        notes: document.getElementById("notesInput").value.trim(),
        applied_date: document.getElementById("dateInput").value
      });

      modalOverlay.classList.remove("active");
      InternMitra.showToast("Application saved! 🎉", "success");

      // Refresh table and stats
      loadApplications();
      loadStats();

    } catch (e) {
      InternMitra.showToast("Error saving application.", "error");
    }

    saveAppBtn.textContent = "Save Application";
    saveAppBtn.disabled = false;
  });

  // ── Load Applications ──────────────────────────────────────────────────────
  async function loadApplications() {
    try {
      const data = await InternMitra.apiCall(`/tracker/list/${userId}`);

      if (!data || data.length === 0) {
        emptyState.style.display = "block";
        trackerTable.style.display = "none";
        return;
      }

      emptyState.style.display = "none";
      trackerTable.style.display = "table";

      trackerBody.innerHTML = data.map(app => `
        <tr id="row-${app.id}">
          <td>
            <strong style="color:var(--dark);">${app.company}</strong>
          </td>
          <td style="color:var(--gray-700);">${app.role}</td>
          <td>
            <select class="status-select status-${app.status}"
              onchange="updateStatus(${app.id}, this.value, this)">
              <option ${app.status === "Applied"   ? "selected" : ""}>Applied</option>
              <option ${app.status === "Interview" ? "selected" : ""}>Interview</option>
              <option ${app.status === "Offer"     ? "selected" : ""}>Offer</option>
              <option ${app.status === "Rejected"  ? "selected" : ""}>Rejected</option>
            </select>
          </td>
          <td style="color:var(--gray-500);font-size:0.85rem;">
            ${InternMitra.formatDate(app.applied_date)}
          </td>
          <td style="color:var(--gray-600);font-size:0.85rem;max-width:180px;">
            ${InternMitra.truncate(app.notes, 50)}
          </td>
          <td>
            <button class="btn btn-danger"
              style="font-size:0.75rem;padding:5px 10px;"
              onclick="deleteApplication(${app.id})">
              🗑 Delete
            </button>
          </td>
        </tr>
      `).join("");

    } catch (e) {
      InternMitra.showToast("Error loading applications.", "error");
    }
  }

  // ── Load Stats ─────────────────────────────────────────────────────────────
  async function loadStats() {
    try {
      const stats = await InternMitra.apiCall(`/tracker/stats/${userId}`);
      document.getElementById("statApplied").textContent   = stats.Applied   || 0;
      document.getElementById("statInterview").textContent = stats.Interview  || 0;
      document.getElementById("statOffer").textContent     = stats.Offer      || 0;
      document.getElementById("statRejected").textContent  = stats.Rejected   || 0;
      document.getElementById("statTotal").textContent     = stats.total      || 0;
    } catch (e) {
      console.error("Error loading stats:", e);
    }
  }

  // ── Update Status ──────────────────────────────────────────────────────────
  window.updateStatus = async (appId, newStatus, selectEl) => {
    // Update select color immediately
    selectEl.className = `status-select status-${newStatus}`;

    try {
      await InternMitra.apiCall(`/tracker/update/${appId}`, "PUT", {
        status: newStatus,
        notes: ""
      });

      InternMitra.showToast(`Status updated to "${newStatus}"`, "success");
      loadStats(); // Refresh stats

    } catch (e) {
      InternMitra.showToast("Error updating status.", "error");
    }
  };

  // ── Delete Application ─────────────────────────────────────────────────────
  window.deleteApplication = async (appId) => {
    if (!confirm("Are you sure you want to delete this application?")) return;

    try {
      await InternMitra.apiCall(`/tracker/delete/${appId}`, "DELETE");

      // Remove row from table smoothly
      const row = document.getElementById(`row-${appId}`);
      if (row) {
        row.style.opacity = "0";
        row.style.transition = "opacity 0.3s";
        setTimeout(() => row.remove(), 300);
      }

      InternMitra.showToast("Application deleted.", "success");
      loadStats();

      // Check if table is now empty
      setTimeout(() => {
        if (trackerBody.children.length === 0) {
          emptyState.style.display = "block";
          trackerTable.style.display = "none";
        }
      }, 400);

    } catch (e) {
      InternMitra.showToast("Error deleting application.", "error");
    }
  };

  // ── Clear Form ─────────────────────────────────────────────────────────────
  function clearForm() {
    document.getElementById("companyInput").value = "";
    document.getElementById("roleInput").value    = "";
    document.getElementById("statusInput").value  = "Applied";
    document.getElementById("dateInput").value    = new Date().toISOString().split("T")[0];
    document.getElementById("notesInput").value   = "";
  }

});