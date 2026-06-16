const API = "http://127.0.0.1:8000/students";

// ── Load all students into the table ──
async function loadStudents() {
    const tbody = document.getElementById("student-table-body");
    tbody.innerHTML = `<tr><td colspan="8" class="empty">Loading...</td></tr>`;

    const res = await fetch(API + "/");
    const students = await res.json();

    if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty">No students found. Add one above!</td></tr>`;
        return;
    }

    tbody.innerHTML = students.map(s => `
        <tr>
            <td>${s.id}</td>
            <td>${s.name}</td>
            <td>${s.roll_no}</td>
            <td>${s.email}</td>
            <td>${s.phone || "—"}</td>
            <td>${s.department || "—"}</td>
            <td>${s.year ? s.year + " yr" : "—"}</td>
            <td>
                <button class="btn-edit" onclick="editStudent(${s.id})">✏️ Edit</button>
                <button class="btn-delete" onclick="deleteStudent(${s.id})">🗑️ Delete</button>
            </td>
        </tr>
    `).join("");
}

// ── Handle form submit (Create or Update) ──
document.getElementById("student-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("student-id").value;
    const data = {
        name:       document.getElementById("name").value.trim(),
        roll_no:    document.getElementById("roll_no").value.trim(),
        email:      document.getElementById("email").value.trim(),
        phone:      document.getElementById("phone").value.trim() || null,
        department: document.getElementById("department").value.trim() || null,
        year:       document.getElementById("year").value ? parseInt(document.getElementById("year").value) : null,
    };

    const isUpdate = id !== "";
    const url    = isUpdate ? `${API}/${id}` : `${API}/`;
    const method = isUpdate ? "PUT" : "POST";

    const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    const result = await res.json();
    const msg = document.getElementById("form-message");

    if (res.ok) {
        msg.textContent = isUpdate ? "✅ Student updated!" : "✅ Student added!";
        msg.className = "success";
        resetForm();
        loadStudents();
    } else {
        msg.textContent = "❌ " + (result.detail || "Something went wrong");
        msg.className = "error";
    }
});

// ── Fill form with student data for editing ──
async function editStudent(id) {
    const res = await fetch(`${API}/${id}`);
    const s = await res.json();

    document.getElementById("student-id").value  = s.id;
    document.getElementById("name").value        = s.name;
    document.getElementById("roll_no").value     = s.roll_no;
    document.getElementById("email").value       = s.email;
    document.getElementById("phone").value       = s.phone || "";
    document.getElementById("department").value  = s.department || "";
    document.getElementById("year").value        = s.year || "";

    document.getElementById("form-title").textContent  = "✏️ Edit Student";
    document.getElementById("submit-btn").textContent  = "💾 Update Student";
    document.getElementById("cancel-btn").classList.remove("hidden");

    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Delete a student ──
async function deleteStudent(id) {
    if (!confirm(`Are you sure you want to delete student ID ${id}?`)) return;

    const res = await fetch(`${API}/${id}`, { method: "DELETE" });

    if (res.ok) {
        loadStudents();
    } else {
        alert("Failed to delete student.");
    }
}

// ── Reset form back to Add mode ──
function resetForm() {
    document.getElementById("student-form").reset();
    document.getElementById("student-id").value        = "";
    document.getElementById("form-title").textContent  = "Add New Student";
    document.getElementById("submit-btn").textContent  = "➕ Add Student";
    document.getElementById("cancel-btn").classList.add("hidden");
    document.getElementById("form-message").textContent = "";
}

// Load students on page open
loadStudents();
