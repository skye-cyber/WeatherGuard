document.addEventListener("DOMContentLoaded", function () {
    const guestLoginBtn = document.getElementById("guestLoginBtn");

    if (guestLoginBtn) {
        guestLoginBtn.addEventListener("click", function (event) {
            event.stopPropagation();
             window.HandleLoading('show', 'Just a moment. Logging in ...')
            fetch("/api/guest-login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            })
            .then(response => {
                if (response.status === 200) {
                    window.location.href = "/home/";
                } else {
                     window.HandleLoading('hide')
                      window.displayStatus('Error', `Failed to login: ${error}`)
                    alert("Guest login failed. Please try again.");
                }
            });
        });
    }
});
