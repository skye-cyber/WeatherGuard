        $(document).ready(function() {
            $('#signup-form').on('submit', function(event) {
                event.preventDefault();

                const locationName = $('#location_names').val();
                if (locationName) {
                    $.ajax({
                        url: '{% url "geocode_location" %}',
                        method: 'GET',
                        data: {
                            location: locationName
                        },
                        success: function(response) {
                            if (response) {
                                alert(response)
                                $('#location_coordinates').val(response);

                                $('#signup-form').unbind('submit').submit();
                            } else {
                                alert('Location not found. Please try again.');
                            }
                        },
                        error: function() {
                            alert('An error occurred. Please try again.');
                        }
                    });
                } else {
                    alert('Please enter a location.');
                }
            });
        });
