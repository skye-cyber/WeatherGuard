document.addEventListener('DOMContentLoaded', ()=>{
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
})
