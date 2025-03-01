document.addEventListener('DOMContentLoaded', ()=>{
    const user = document.getElementById('user-display');
    if(user.textContent.toLowerCase()==='guest101'){
        OrientGuest(user.textContent);
    }

    const paneButton = document.getElementById('togglePanel');
    const sidePanel = document.getElementById('sidePanel');


    paneButton.addEventListener('click', function(){
        sidePanel.classList.toggle("-translate-x-full");
        sidePanel.classList.toggle("-translate-x-1");
    })

    const settingsButton = document.getElementById('settings-button');
    const settingsModal = document.getElementById('settings-modal');

    settingsButton.addEventListener('click', function(){
        settingsModal.classList.toggle("translate-x-full");
        settingsModal.classList.toggle("translate-x-1");
    })

    const closeSettingsX = document.getElementById('close-settingsX');
    closeSettingsX.addEventListener('click', function(){
        settingsModal.classList.toggle("translate-x-full");
        settingsModal.classList.toggle("translate-x-1");
    })

    const openModalBtn = document.getElementById('openSettingsManBtn');
    const modalBackdrop = document.getElementById('modalBackdrop');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeModalBtnFooter = document.getElementById('closeModalBtnFooter');

    openModalBtn.addEventListener('click', () => {
        modalBackdrop.classList.toggle("translate-x-full");
        modalBackdrop.classList.toggle("translate-x-1");
    });

    closeModalBtn.addEventListener('click', () => {
        modalBackdrop.classList.toggle("translate-x-full");
        modalBackdrop.classList.toggle("translate-x-1");
    });

    closeModalBtnFooter.addEventListener('click', () => {
        modalBackdrop.classList.toggle("translate-x-full");
        modalBackdrop.classList.toggle("translate-x-1");
    });

    const AddlocationBt = document.getElementById('save-location');
    const locationInput = document.getElementById('location-input');
    AddlocationBt.addEventListener('click', () =>{
        HandleLoading("show", "Working on it! Standby...");
        const locationValue = locationInput.value;
        const locationData = {'location_name': locationValue}

        AddLocation()
        async function AddLocation(){
            try{
                const response = await fetch('/new-location/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
                    },
                    body: JSON.stringify(locationData)
                });

                const response_data = await response.json()

                HandleLoading('hide')

                if (response.status===201){
                    displayStatus('Location added Successfully.', 'success');
                }else{
                    const msg = response_data.statusText ? response_data.statusText : (response.statusText ? response.statusText : "" );
                    displayStatus(`The operation to add location failed! ${msg}`, 'error')
                }

            }catch(error){
                HandleLoading('hide');
                displayStatus(error, 'error')
                console.log("Error while submitting the form", error);
            }
        }

    });

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


    function OrientGuest(username){
        //
    }

    window.displayStatus=displayStatus;
    window.hideStatus=hideStatus;
    window.HandleLoading = HandleLoading;
});
