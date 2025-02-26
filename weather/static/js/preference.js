document.addEventListener('DOMContentLoaded', ()=>{
    const sms_notification = document.getElementById('sms-notification');
    const email_notification = document.getElementById('email-notification');
    const low_verbosity = document.getElementById('low-verbosity');
    const medium_verbosity = document.getElementById('medium-verbosity');
    const high_verbosity = document.getElementById('high-verbosity');
    const hourly_frequency = document.getElementById('hourly-notification');
    const daily_frequency = document.getElementById('daily-notification');
    const weekly_frequency = document.getElementById('weekly-notification');

    fetchPreferences();

    async function fetchPreferences(){
        try{
            const response = await fetch('/get-user-preferences/', {
                method: 'Get',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.status === 200){
                const data = await response.json()
                SetPreferences(data.data);
                }
        }catch(error){
            console.log(error)
        }
    }

    function SetPreferences(data){
        data.notification_medium.toLowerCase() === "sms" ? sms_notification.checked = true : sms_notification.checked = false;
        data.notification_medium.toLowerCase() === "email" ? email_notification.checked = true : email_notification.checked = false;
        data.verbosity.toLowerCase()==="low" ? low_verbosity.checked = true : low_verbosity.checked = false;
        data.verbosity.toLowerCase()==="medium" ? medium_verbosity.checked = true : medium_verbosity.checked = false;
        data.verbosity.toLowerCase()==="high" ? high_verbosity.checked = true : high_verbosity.checked = false;
        data.notification_frequency.toLowerCase() === "hourly" ? hourly_frequency.checked = true : hourly_frequency.checked = false;
        data.notification_frequency.toLowerCase() === "daily" ? daily_frequency.checked = true : daily_frequency.checked = false;
        data.notification_frequency.toLowerCase() === "weekly" ? weekly_frequency.checked = true : weekly_frequency.checked = false;
    }

    async function postPrefChange(data){
        try{
            const response = await fetch('/set-user-preferences/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                },
                body: JSON.stringify(data),
            });

            if (response.status === 200){
                // Show success Modal
                window.HandleLoading('hide');
                HandleStatusModal('Preferences Update successfully.' , 'show', 'success');

            }else{
                //Show Error modal
                window.HandleLoading('hide');
                HandleStatusModal(`Error Updating preferences: ${response.statsusText ? response.statsusText : ""}` , 'show', 'error');
            }
        }catch(error){
            window.HandleLoading('hide');
            console.log(error)
        }
    }

    // Add change event listener
    const saveSettings = document.getElementById('save-settings');

    const parentVerbosity = document.getElementById('verbosity');

    const verbosity = parentVerbosity.querySelector('input[name="verbosity"]:checked').value;

    const parentFrequency = document.getElementById('notification-frequency');
    const frequency = parentFrequency.querySelector('input[name="notification-frequency"]:checked').value;

    const parentMedium = document.getElementById('notification-medium');
    const medium = parentMedium.querySelector('input[name="notification-medium"]:checked').value;

    saveSettings.addEventListener('click', () =>{
        try{
            window.HandleLoading('show');
            data = {
                "notification_medium": medium,
                "notification_frequency": frequency,
                "verbosity": verbosity,
            }
            postPrefChange(data);
        }catch(error){
            console.log(error);
            window.HandleLoading('hide');
        }
    });

    function HandleStatusModal(message=null, task, type){
        const modal = type==='success' ? document.getElementById("success-modal") : document.getElementById("errorModal");
        const modalBox = type==='success' ? document.getElementById('successBoxBody') : document.getElementById('errorBox');
        if(message){
            const mesSection = type==='success' ? document.getElementById('SuccessMsg') : document.getElementById('error-message');
            mesSection.textContent = message;
        }

        if(type === "success"){
            // Display success modal
            if (task==="show"){
                modal.classList.remove('hidden');
                modalBox.classList.remove('animate-exit');
                modalBox.classList.add('animate-enter');
            }else{
                // Hide success modal
                modalBox.classList.remove('animate-enter');
                modalBox.classList.add('animate-exit');
                setTimeout( ()=> {
                    modal.classList.add('hidden');
                }, 310)
            }
        }else{
            if (task==="show"){
                // Display error modal
                modal.classList.remove('hidden');
                modalBox.classList.remove('animate-exit');
                modalBox.classList.add('animate-enter');
            }else{
                // Hide error modal
                modalBox.classList.add('animate-enter');
                modalBox.classList.add('animate-exit');
                setTimeout( ()=> {
                    modal.classList.add('hidden');
                }, 310)
            }
        }
    }
    document.getElementById('CloseSucsessModal').addEventListener('click', () =>{
        HandleStatusModal(null, 'hide', 'success');
    })
});
