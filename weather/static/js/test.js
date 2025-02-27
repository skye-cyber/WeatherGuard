document.addEventListener('DOMContentLoaded', function() {
    const bt = document.getElementById("testbt");
    bt.addEventListener('click', ()=>{
        console.log("Requesting notification")
        TestNotify();
    })
    async function TestNotify(){
        try{
            // Send a GET request to the Django view
            const response = await fetch('/notify-now/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
            });
            console.log(response)
            // Check if the response is OK (status code 200-299)
            if (!response.status===200) {
                console.log("Success!")
                const data = await response.json();
                console.log(data)
                console.log(data.message)
            }
        console.log("Notification logic end")
    } catch (error) {
        console.log(error)
        return null;
    }
}

});
