document.addEventListener("DOMContentLoaded", function () {
    const guestLoginBtn = document.getElementById("guestLoginBtn");

    if (guestLoginBtn) {
        guestLoginBtn.addEventListener("click", function (event) {
            event.stopPropagation();
            HandleLoading('show', 'Just a moment. Logging in ...')
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
                    HandleLoading('hide')
                    displayStatus('Error', `Failed to login: ${error}`)
                    alert("Guest login failed. Please try again.");
                }
            });
        });
    }


    function HandleLoading(task, message=null){

        const loadingModal = document.getElementById('loadingModal');
        const modalMainBox = document.getElementById('modalMainBox');
        if (task==="show"){
            if (message){
                const msgBox = document.getElementById('loadingMSG');
                msgBox.textContent = message;
            }
            loadingModal.classList.remove('hidden');
            modalMainBox.classList.remove('animate-exit');
            modalMainBox.classList.add('animate-enter')
        }else{
            modalMainBox.classList.remove('animate-enter')
            modalMainBox.classList.add('animate-exit');
            setTimeout( ()=> {
                loadingModal.classList.add('hidden');
            }, 310)
        }
    }

    function displayStatus(message=null, type='success'){
        const modal = type==='success' ? document.getElementById('successModal') : document.getElementById('errorModal');
        const box = type==='success' ? document.getElementById('successBox') : document.getElementById('errorBox');
        if(message){
            const mesSection = type==='success' ? document.getElementById('success-message') : document.getElementById('error-message');
            mesSection.textContent = message;
        }
        modal.classList.remove('hidden');
        box.classList.remove('animate-exit');
        box.classList.add('animate-enter')
    }

    function hideStatus(type){
        const modal = type==='success' ? document.getElementById('successModal') : document.getElementById('errorModal');
        const box = type==='success' ? document.getElementById('successBox') : document.getElementById('errorBox');

        box.classList.remove('animate-enter')
        box.classList.add('animate-exit');
        setTimeout( ()=> {
            modal.classList.add('hidden');
        }, 310)
    }
});
