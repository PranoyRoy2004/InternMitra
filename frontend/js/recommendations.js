// recommendations.js - Handles the recommendations page logic
// Sends user profile to backend and renders AI recommendations

document.addEventListener("DOMContentLoaded", () => {

  const skillsInput      = document.getElementById("skillsInput");
  const skillTagsEl      = document.getElementById("skillTags");
  const interestsInput   = document.getElementById("interestsInput");
  const experienceInput  = document.getElementById("experienceInput");
  const getRecsBtn       = document.getElementById("getRecsBtn");
  const emptyState       = document.getElementById("emptyState");
  const loadingState     = document.getElementById("loadingState");
  const resultsContent   = document.getElementById("resultsContent");
  const adviceText       = document.getElementById("adviceText");
  const recCards         = document.getElementById("recCards");

  // ── Skills Tag System ──────────────────────────────────────────────────────
  let skills = [];

  // When user presses comma or Enter, add a skill tag
  skillsInput.addEventListener("keydown", (e) => {
    if (e.key === "," || e.key === "Enter") {
      e.preventDefault();
      const skill = skillsInput.value.trim().replace(",", "");
      if (skill && !skills.includes(skill)) {
        skills.push(skill);
        renderSkillTags();
      }
      skillsInput.value = "";
    }
  });

  // Also handle paste — split by comma
  skillsInput.addEventListener("blur", () => {
    const value = skillsInput.value.trim();
    if (value) {
      value.split(",").forEach(s => {
        const skill = s.trim();
        if (skill && !skills.includes(skill)) skills.push(skill);
      });
      renderSkillTags();
      skillsInput.value = "";
    }
  });

  function renderSkillTags() {
    skillTagsEl.innerHTML = skills.map((skill, i) => `
      <span class="badge badge-primary" style="cursor:pointer;gap:6px;">
        ${skill}
        <span onclick="removeSkill(${i})" style="font-weight:700;opacity:0.7;">×</span>
      </span>
    `).join("");
  }

  // Make removeSkill globally accessible
  window.removeSkill = (index) => {
    skills.splice(index, 1);
    renderSkillTags();
  };

  // ── Get Recommendations ────────────────────────────────────────────────────
  getRecsBtn.addEventListener("click", async () => {

    // Collect any remaining text in the input as a skill
    const remaining = skillsInput.value.trim();
    if (remaining) {
      remaining.split(",").forEach(s => {
        const skill = s.trim();
        if (skill && !skills.includes(skill)) skills.push(skill);
      });
      skillsInput.value = "";
      renderSkillTags();
    }

    // Validate
    if (skills.length === 0) {
      InternMitra.showToast("Please enter at least one skill.", "error");
      return;
    }

    if (!interestsInput.value.trim()) {
      InternMitra.showToast("Please describe your interests.", "error");
      return;
    }

    // Show loading
    emptyState.style.display   = "none";
    loadingState.style.display = "block";
    resultsContent.style.display = "none";
    getRecsBtn.disabled = true;
    getRecsBtn.textContent = "Analyzing...";

    try {
      const data = await InternMitra.apiCall("/recommendations/get", "POST", {
        skills: skills,
        interests: interestsInput.value.trim(),
        experience_level: experienceInput.value,
        user_id: InternMitra.getUserId()
      });

      // Render results
      renderResults(data);
      InternMitra.showToast("Recommendations ready! 🎉", "success");

    } catch (error) {
      InternMitra.showToast("Error getting recommendations. Is the backend running?", "error");
      emptyState.style.display = "block";
      loadingState.style.display = "none";
    }

    getRecsBtn.disabled = false;
    getRecsBtn.textContent = "✨ Get AI Recommendations";
  });

  // ── Render Results ─────────────────────────────────────────────────────────
  function renderResults(data) {
    loadingState.style.display   = "none";
    resultsContent.style.display = "block";

    // AI Advice
    adviceText.textContent = data.advice || "Focus on building projects and applying consistently.";

    // Recommendation Cards
    recCards.innerHTML = data.recommendations.map((rec, i) => `
      <div class="card" style="margin-bottom:1rem;border-left:4px solid var(--primary);animation:fadeUp 0.4s ease ${i * 0.1}s both;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">
          <div>
            <h3 style="font-size:1.1rem;font-weight:700;color:var(--dark);">
              ${rec.role}
            </h3>
            <span style="color:var(--gray-500);font-size:0.85rem;">📍 ${rec.company_type}</span>
          </div>
          <span class="badge ${getDifficultyBadge(rec.difficulty)}">${rec.difficulty}</span>
        </div>

        <div style="margin-bottom:1rem;">
          <p style="font-size:0.8rem;font-weight:600;color:var(--gray-500);margin-bottom:6px;">SKILLS REQUIRED</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px;">
            ${rec.skills_required.map(s => `<span class="badge badge-gray">${s}</span>`).join("")}
          </div>
        </div>

        <div>
          <p style="font-size:0.8rem;font-weight:600;color:var(--gray-500);margin-bottom:8px;">LEARNING ROADMAP</p>
          <ol style="padding-left:1.2rem;color:var(--gray-700);font-size:0.875rem;line-height:2;">
            ${rec.learning_roadmap.map(step => `<li>${step}</li>`).join("")}
          </ol>
        </div>

        <div style="margin-top:1rem;display:flex;gap:8px;flex-wrap:wrap;">
          <a href="chat.html" class="btn btn-outline" style="font-size:0.8rem;padding:7px 14px;">
            💬 Ask AI about this role
          </a>
          <button class="btn btn-ghost" style="font-size:0.8rem;padding:7px 14px;"
            onclick="saveToTracker('${rec.role}', '${rec.company_type}')">
            📌 Save to Tracker
          </button>
        </div>
      </div>
    `).join("");
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  function getDifficultyBadge(difficulty) {
    const map = {
      "Beginner": "badge-success",
      "Intermediate": "badge-warning",
      "Advanced": "badge-danger"
    };
    return map[difficulty] || "badge-gray";
  }

  // Save a recommended role directly to the tracker
  window.saveToTracker = async (role, companyType) => {
    try {
      await InternMitra.apiCall("/tracker/add", "POST", {
        user_id: InternMitra.getUserId(),
        company: companyType,
        role: role,
        status: "Applied",
        notes: "Added from AI recommendations",
        applied_date: new Date().toISOString().split("T")[0]
      });
      InternMitra.showToast(`"${role}" saved to tracker! 📌`, "success");
    } catch (e) {
      InternMitra.showToast("Could not save to tracker.", "error");
    }
  };

  // ── CSS animation ──────────────────────────────────────────────────────────
  const style = document.createElement("style");
  style.textContent = `
    @keyframes fadeUp {
      from { opacity:0; transform:translateY(16px); }
      to   { opacity:1; transform:translateY(0); }
    }
  `;
  document.head.appendChild(style);

});