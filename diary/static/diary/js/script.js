document.addEventListener("DOMContentLoaded", function () {
  const toggles = document.querySelectorAll(".toggle-password");

  toggles.forEach((toggle) => {
    toggle.addEventListener("click", function () {
      const input = this.closest(".input-group").querySelector("input");
      const icon = this.querySelector("i");

      if (input) {
        input.type = input.type === "password" ? "text" : "password";
        icon.classList.toggle("fa-eye");
        icon.classList.toggle("fa-eye-slash");
      }
    });
  });
});


  document.addEventListener('DOMContentLoaded', function () {
    const toast = document.querySelector('.toast');

    if (toast) {
      setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
          toast.remove();
        }, 600); // Match the exit animation duration
      }, 3000); // Wait 3s before dismiss
    }
  });