document.addEventListener('DOMContentLoaded', function() {
    async function SearchByLoc(location){
        try{
            console.log(location)
            window.HandleLoading('show', 'Content will AutoUpdate on search completion. Searching ...');
            // Send a GET request to the Django view
            const response = await fetch('/api/search_location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ 'loc_name': location }),
            });

            // Check if the response is OK (status code 200-299)
            if (response.status===200) {
                window.HandleLoading('hide');
                window.displayStatus('Search completed successfully', 'success');
                console.log("Success!")
                const data = await response.json();
                if(data.html){
                    // Replace the entire page with the new rendered HTML.
                    setTimeout(()=>{
                        document.open();
                        document.write(data.html);
                        document.close();
                    }, 1000)
                }
            }else{
                window.HandleLoading('hide');
                window.displayStatus(`Search unsuccessful: ${response.statusText}`, 'error');
                console.log(response.statusText)
            }
        } catch (error) {
            window.HandleLoading('hide');
            window.displayStatus(`Search unsuccessful: ${error}`, 'error');
            console.log(error)
            return null;
        }
    }

    const search_bar = document.getElementById('search_bar');
    //search_bar.addEventListener('click', SearchByLoc(search_bar.textContent));

    search_bar.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            SearchByLoc(search_bar.value)
        }
    });
});
