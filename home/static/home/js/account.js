document.addEventListener("DOMContentLoaded", function() {
  const form = document.getElementById("profileForm");
  const editBtn = document.getElementById("editBtn");
  const actionButtons = document.getElementById("actionButtons");
  const inputs = form.querySelectorAll("input, select");
  const dobInput = document.getElementById("dob");

  // Khi bấm nút "Cập nhật thông tin"
  editBtn.addEventListener("click", function() {
    inputs.forEach(input => {
      if (input.id !== "email" && input.id !== "username") {
        input.removeAttribute("disabled");
      }
    });

    actionButtons.innerHTML = `
      <button type="submit" class="submit-btn">Lưu</button>
      <button type="button" class="cancel-btn" id="cancelBtn">Quay lại</button>
    `;

    // Nút Quay lại
    document.getElementById("cancelBtn").addEventListener("click", function() {
      inputs.forEach(input => input.setAttribute("disabled", true));
      actionButtons.innerHTML = `<button type="button" class="edit-btn" id="editBtn">Cập nhật thông tin</button>`;
      document.getElementById("editBtn").addEventListener("click", editBtn.click);
    });
  });

  // Trước khi submit form
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    if (confirm("Bạn có muốn đổi thông tin không?")) {
      // Chuyển mm/dd/yyyy -> yyyy-mm-dd
      if (dobInput.value) {
        let parts = dobInput.value.split("/");
        if (parts.length === 3) {
          let mm = parts[0].padStart(2, "0");
          let dd = parts[1].padStart(2, "0");
          let yyyy = parts[2];
          dobInput.value = `${yyyy}-${mm}-${dd}`;
        }
      }
      form.submit();
    }
  });
});