// Pre-render the URL in the template
document.addEventListener('DOMContentLoaded', function() {
    const submit = document.getElementById('submit-register');
    const processingModal = document.getElementById('processingModal');
    submit.addEventListener('click', function() {
        // Ensure HTML5 validation rules are enforced
        if (!form.checkValidity()) {
            form.reportValidity(); // Show validation messages
            return; // Stop further execution if form is invalid
        }
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
            if (data.coordinates) {
                console.log('Coordinates:', data);
                coord.value = data.coordinates;

                const phone = document.getElementById('phone');
                const code = document.getElementById('country-code').value;
                const _phone = `${code}${phone.value}`;

                // Call phone number regex validator
                const isvalid = validatePhoneNumber(_phone, code);
                if (isvalid.status) {
                    phone.value = isvalid.phoneNumber;
                    console.log(phone.value)
                    //phone.textContent = isvalid.phoneNumber;
                    //form.submit();
                    register(form)
                    phone.value = _phone;
                } else {
                    showModal(`Invalid phone number got:'${isvalid.phoneNumber}'`);
                    phone.value = _phone;
                }
            } else if (data.error) {
                phone.value = _phone;
                console.log(error)
            }
        });

    });

    function validatePhoneNumber(phoneNumber, code = null) {
        const phoneNumberPattern = /^\+\d{9,15}$/;
        let isValid = phoneNumberPattern.test(phoneNumber);

        if (code === '+254' && phoneNumber.length > 13) {
            isValid = false;
            if (phoneNumber.length === 14 && phoneNumber.substring(4, 5) === '0') {
                phoneNumber = `${phoneNumber.substr(0, 4)}${phoneNumber.substr(5)}`
                isValid = true;
            }
        }
        return { status: isValid, phoneNumber: phoneNumber }
    }

    function validateCoordinates(coordinates) {
        const coordinatesPattern = /^-?\d+(\.\d+)?,-?\d+(\.\d+)?$/;
        return coordinatesPattern.test(coordinates);
    }

    const countryCodeSelect = document.querySelector('#country-code');
    const selectedValue = document.querySelector('#selected-code');
    const customDropdown = document.querySelector('#ParentCustom');
    const selectedText = document.querySelector('#selected-text');
    //const selectedFlag = document.querySelector('#selected-flag');

    fetch('https://restcountries.com/v2/all', {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            // Sort the data by calling codes
            data.sort((a, b) => a.callingCodes[0].localeCompare(b.callingCodes[0]));

            setTimeout(() => {
                // Set default values
                customDropdown.querySelector('[data-value="+254"]').click()
            }, 5000);

            data.forEach(country => {
                // Create an option element for the hidden dropdown
                const option = document.createElement('option');
                option.value = `+${country.callingCodes[0]}`;
                option.textContent = `+${country.callingCodes[0]}`;
                option.setAttribute('data-flag', country.flags.svg);
                countryCodeSelect.appendChild(option);

                // Create a custom dropdown item
                const p = document.createElement('p'); p
                p.setAttribute('data-value', `+${country.callingCodes[0]}`);
                p.setAttribute('data-flag', `+${country.flags.svg}`);
                p.setAttribute('data-text', `+${country.callingCodes[0]} - ${country.name}`);
                p.innerHTML = `<img src="${country.flags.svg}" alt="${country.name} Flag" class="w-5 h-5 mr-3" /> +${country.callingCodes[0]} - ${country.name}`;
                p.classList.add('px-4', 'py-2', 'hover:bg-gray-100', 'flex', 'items-center', 'cursor-pointer');
                customDropdown.appendChild(p);
            });

            // Close the dropdown when clicking outside
            document.addEventListener('click', (event) => {
                if (!event.target.closest('.dropdown-container')) {
                    customDropdown.classList.add('hidden');
                    //document.getElementById('ParentCustom').classList.;
                }
            });

            // Toggle custom dropdown on selected value click
            selectedValue.addEventListener('click', (event) => {
                event.preventDefault();
                customDropdown.classList.toggle('hidden');
            });

            // Handle selection in custom dropdown
            customDropdown.querySelectorAll('p').forEach(p => {
                p.addEventListener('click', () => {
                    const value = p.getAttribute('data-value');
                    //const flag = p.getAttribute('data-flag');
                    //const text = p.getAttribute('data-text');

                    // Set original dropdown value to value of selected element
                    countryCodeSelect.value = value;

                    // Set the selected value
                    selectedText.textContent = value;
                    //selectedFlag.src = flag;
                    //selectedFlag.classList.remove('hidden');

                    // Close the dropdown
                    customDropdown.classList.add('hidden');
                });
            });
        })
        .catch(error => {
            showModal(`Error fetching country codes: Enter phone number with country-code i.e +254****`);
            console.error('Error fetching country codes: ', error);
        });
    window.validateCoordinates = validateCoordinates;
});

async function geocodeLocation(locationName) {
    try {
        const coord = document.getElementById('location_coordinates').textContent;
        console.log("coord", coord)
        if (coord) {
            const isValidCoord = window.validateCoordinates(coord);
            console.log(isValidCoord)
            if (isValidCoord) {
                return { coordinates: coord }
            }
        }
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


function showModal(errorMessage, html = false) {
    const modalErrorMessage = document.getElementById('modal-error-message')
    if (html) {
        modalErrorMessage.innerHTML = errorMessage.innerHTML;
    } else {
        modalErrorMessage.innerText = errorMessage;
    }
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

function register(form) {
    let formData = new FormData(form);

    fetch('/onboard/', {
        method: 'POST',
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success" && data.redirect_url) {
                window.location.href = data.redirect_url; // Follow server's redirect
                return;
            }

            document.getElementById('processingModal').classList.add('hidden');

            if (data.details) throw data.details;

            if (data.errors) {
                console.log("Validation Errors:", data.errors);
                const errors = CreateErrorTemplate(data.errors);
                showModal(errors, true);
            }
        })
        .catch(error => {
            console.error("Error:", error);
            document.getElementById('processingModal').classList.add('hidden');
            const errors = CreateErrorTemplate(error);
            showModal(errors, true);
        });
}



// Function to format and show errors
function CreateErrorTemplate(errors) {
    let errorList = document.createElement("ul");
    errorList.innerHTML = ""; // Clear old errors

    Object.keys(errors).forEach(field => {
        errors[field].forEach(errorMsg => {
            let li = document.createElement("li");
            if (field === 'locations') {
                if (Array.isArray(field) && field.length > 0) {
                    const locationErrors = field[0]; // Extract first object in the array
                    const nameErrors = locationErrors.name ? locationErrors.name.join(', ') : '';
                    const coordinateErrors = locationErrors.coordinates ? locationErrors.coordinates.join(', ') : '';

                    li.textContent = `${field}: ${nameErrors} ${coordinateErrors}`.trim();
                }

            } else {
                li.textContent = `${field}: ${errorMsg}`;
            }
            li.classList.add("text-red-500", "mt-1"); // Tailwind styling
            errorList.appendChild(li);
        });
    });

    return errorList;
}
