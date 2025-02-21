document.addEventListener('DOMContentLoaded', function(){
    document.getElementById('verifyPhoneButton').addEventListener('click', function(){
        document.getElementById('getSMS').submit();
    });
    document.getElementById('verificationForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const statusMSG = document.getElementById('responseMessage');
        // Show the processing modal
        const processingModal = document.getElementById('processingModal');
        processingModal.classList.remove('hidden');

        const verificationCode = document.getElementById('verification_code').value;
        const data = { verification_code: verificationCode };

        VerifySMS(data);

        async function VerifySMS(data){
            try{
                const url = new URL('/verify-sms/', window.location.origin);
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(data)
                });


                if (response.ok) {
                    // Hide processingModal
                    processingModal.classList.add('hidden');
                    // Verification successful
                    statusMSG.innerText = 'Verification successful!';
                    statusMSG.classList.add('text-green-500');
                } else {
                    const errorData = await response.json();
                    // Verification failed
                    statusMSG.innerText = errorData.error;
                    statusMSG.classList.add('text-red-500');
                }

            }catch(error){
                processingModal.classList.add('hidden');
                console.error('Fetch error:', error);
                statusMSG.innerText = 'Failed to verify the code.';
                statusMSG.classList.add('text-red-500');
            };
        }


        // Request Verification code
    });
});
