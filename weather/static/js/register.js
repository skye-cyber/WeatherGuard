// Pre-render the URL in the template
document.addEventListener('DOMContentLoaded', function() {
    const submit = document.getElementById('submit-register');
    const processingModal = document.getElementById('processingModal');
    submit.addEventListener('click', function(){
        // Show processing modal
        processingModal.classList.remove('hidden');
    })
    const form = document.getElementById('signup-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const locationName = document.getElementById('location_name').value;
        const coord = document.getElementById('location_coordinates');
        geocodeLocation(locationName).then(data => {
            console.log(data)
            if (data.coordinates){
                console.log('Coordinates:', data);
                coord.value = data.coordinates;
                form.submit();
            } else if (data.error){
                console.log(error)
            }
        });

    });
});

async function geocodeLocation(locationName) {
    try {
        // Construct the URL with the location query parameter
        const url = new URL('/geocode/', window.location.origin);
        url.searchParams.set('loc_name', locationName);

        // Send a GET request to the Django view
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        // Check if the response is OK (status code 200-299)
        if (!response.ok) {
            console.log(response)
            const errorData = await response.json();
            showModal(errorData.error || 'An error occurred');
        }

        // Parse the JSON response
        const data = await response.json();
        console.log(JSON.stringify(data));
        console.log(JSON.stringify(data.coordinates))
        return data;
    } catch (error) {
        showModal('Fetch error: ' + error.message);
        return null;
    }
}


function showModal(errorMessage) {
    document.getElementById('modal-error-message').innerText = errorMessage;
    // Hide processing modal first
    document.getElementById('processingModal').classList.add('hidden');
    document.getElementById('errorModal').classList.remove('hidden');
    document.getElementById('retryButton').onclick = function() {
        closeModal();
        document.getElementById('submit-register').click();
    };
}

function closeModal() {
    document.getElementById('errorModal').classList.add('hidden');
}
