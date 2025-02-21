document.addEventListener('DOMContentLoaded', function(){
    const resend = document.getElementById('resendEmailButton');
    const email_field = document.getElementById('email-field');
    const statusModal = document.getElementById('statusModal');
    const statusH = document.getElementById('status-head');
    const statusC = document.getElementById('status-content');

    resend.addEventListener('click', function(){
        let secondsElapsed = 0;

        const timerInterval = setInterval(() => {
            secondsElapsed++;
            resend.textContent = `${secondsElapsed}s`;
            console.log(resend.textContent)
        }, 1000);
        clearInterval(timerInterval);
        secondsElapsed = null;

        resend.classList.add('bg-gray-300');
        resend.classList.remove('bg-green-400');
        setTimeout(() => {
            resend.classList.remove('bg-gray-300');
            resend.classList.add('bg-green-400');
        }, 5000);

        //clearTimeout(resendTimeout);

        email = email_field.value
        const data = { email: email };
        EmailResendRequest(data);
        async function EmailResendRequest(email){
            try{
                const url = new URL('/resend-email/', window.location.origin);
                //url.searchParams.set('email', email);
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                    },
                    body: JSON.stringify(email)
                });

                if (response.ok) {
                    statusModal.classList.remove('hidden');
                } else {
                    const errorData = await response.json();
                    const errorTimeout = setTimeout(() => {
                        statusH.textContent = 'Verification Email not Sent';
                        statusC.textContent = errorData.error;
                        statusModal.classList.remove('hidden');
                    }, 5000);
                    clearTimeout(errorTimeout);
                }

                }catch(error){
                console.error('Fetch error:', error);
                const errorTimeout = setTimeout(() => {
                    statusH.textContent = 'Verification Email not Sent';
                    statusC.textContent = error;
                    statusModal.classList.remove('hidden');
                }, 5000);
                clearTimeout(errorTimeout);
            }
        }
    });
});
