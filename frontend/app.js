const API = "http://localhost:5000/api";

function showSection(id, button) {
  document.querySelectorAll(".section").forEach(s => s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
  document.querySelectorAll("nav button").forEach(b => b.classList.remove("active"));
  button.classList.add("active");
  if (id === "students") loadStudents();
  if (id === "risk") loadRisk();
}

async function checkHealth() {
  try {
    const r = await fetch(`${API}/health`);
    if (!r.ok) throw new Error();
    document.getElementById("status").textContent = "Backend Online";
    document.getElementById("status").className = "online";
  } catch {
    document.getElementById("status").textContent = "Backend Offline";
  }
}

async function loadDashboard() {
  const r = await fetch(`${API}/dashboard`);
  const d = await r.json();
  document.getElementById("total").textContent = d.total_students;
  document.getElementById("riskCount").textContent = d.at_risk_students;
  document.getElementById("avgAttendance").textContent = `${d.average_attendance}%`;
  document.getElementById("avgMarks").textContent = d.average_marks;
}

async function loadStudents() {
  try {
    const r = await fetch(`${API}/students`);

    if (!r.ok) {
      throw new Error("Unable to load student records");
    }

    const students = await r.json();
    const table = document.getElementById("studentTable");

    if (!students.length) {
      table.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center;">
            No student records found.
          </td>
        </tr>
      `;
      return;
    }

    table.innerHTML = students.map(s => `
      <tr>
        <td>${s.id}</td>
        <td>${s.name}</td>
        <td>${s.department}</td>
        <td>${s.email}</td>
        <td>${s.attendance}%</td>
        <td>${s.marks}</td>
        <td>
          <button class="delete" onclick="deleteStudent(${s.id})">
            Delete
          </button>
        </td>
      </tr>
    `).join("");

  } catch (error) {
    document.getElementById("studentTable").innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center;">
          Unable to load student records.
        </td>
      </tr>
    `;
    console.error(error);
  }
}

async function loadRisk() {
  const r = await fetch(`${API}/risk`);
  const students = await r.json();
  const box = document.getElementById("riskList");
  if (!students.length) {
    box.innerHTML = '<div class="panel">No academically at-risk students.</div>';
    return;
  }
  box.innerHTML = students.map(s => `
    <div class="risk-card">
      <strong>${s.name}</strong>
      <span>${s.department}</span>
      <span>Attendance: ${s.attendance}%</span>
      <span>Marks: ${s.marks}</span>
    </div>`).join("");
}

async function deleteStudent(id) {
  if (!confirm("Delete this student?")) return;
  await fetch(`${API}/students/${id}`, { method: "DELETE" });
  loadStudents();
  loadDashboard();
}

document.getElementById("studentForm").addEventListener("submit", async e => {
  e.preventDefault();
  const data = {
    name: document.getElementById("name").value,
    department: document.getElementById("department").value,
    email: document.getElementById("email").value,
    attendance: Number(document.getElementById("attendance").value),
    marks: Number(document.getElementById("marks").value)
  };
  const r = await fetch(`${API}/students`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(data)
  });
  const msg = document.getElementById("formMessage");
  if (r.ok) {
    msg.textContent = "Student added successfully.";
    e.target.reset();
    loadDashboard();
  } else {
    const err = await r.json();
    msg.textContent = err.error || "Unable to add student.";
  }
});

checkHealth();
loadDashboard();
