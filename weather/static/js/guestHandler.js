document.addEventListener('DOMContentLoaded', function() {
    async function TestNotify(email=null){
        window.HandleLoading('show', 'Requesting email, standby...')
        try{
            // Send a GET request to the Django view
            const response = await fetch('/api/notify-now/', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: email ? JSON.stringify({ 'email':email }) : undefined,
            });

            // Check if the response is OK (status code 200-299)
            if (response.status===200) {
                window.HandleLoading('hide');
                window.displayStatus('Email has been sent successfully', 'success');
                console.log("Success!")
                const data = await response.json();
                //console.log(data)
                console.log(data.message)
            }else{
                window.HandleLoading('hide');
                window.displayStatus(`Error sending email: ${response.statusText}`, 'error');
                console.log(response.statusText)
            }
    } catch (error) {
        console.log(error)
        window.HandleLoading('hide');
        window.displayStatus(`Error requesting email: ${error}`, 'error');
        return null;
    }
}

const modal = document.getElementById("emailModal");
const emailModalBox = document.getElementById("emailModalBox");
const closeModal = document.getElementById("closeEmailModal");
const submitEmail = document.getElementById("submitEmail");
const EmailField = document.getElementById("userEmail");

// Send email weather now
const email_bt = document.getElementById("email-weather-now");
email_bt.addEventListener("click", async () => {
    try {
        const email = await GetEmail();
        if (email === "cancel") {
            return;
        }
        TestNotify(email);
    } catch (error) {
        window.displayStatus(`Error handling email request: ${error}`, 'error');
        console.error("Error getting email:", error);
    }
});

async function GetEmail() {
    const user = document.getElementById("user-display");
    if (user.textContent.toLowerCase() !== "guest101") {
        console.log(user.textContent);
        return null;
    }

    ShowMailModal();

    return new Promise((resolve) => {
        closeModal.addEventListener("click", () => {
            HideMailModal();
            resolve("cancel");
        });

        submitEmail.addEventListener("click", () => {
            const email = EmailField.value;
            HideMailModal();
            resolve(email);
        });
    });
}



function ShowMailModal(){
    modal.classList.remove('hidden');
    emailModalBox.classList.remove('animate-exit');
    emailModalBox.classList.add('animate-enter')

}

function HideMailModal(){
    emailModalBox.classList.remove('animate-enter')
    emailModalBox.classList.add('animate-exit');
    setTimeout( ()=> {
        modal.classList.add('hidden');
    }, 310)
}
});
