// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    var submitButton = document.getElementById('submitButton');
    submitButton.onclick = function(event) {
        event.preventDefault();  // Prevent the default form submission

        // Get selected player names
        var player1Name = document.getElementById('player1_name').value;
        var player2Name = document.getElementById('player2_name').value;

        // Ensure both players are selected
        if (!player1Name || !player2Name) {
            console.error('Please select two players');
            return;
        }

        // AJAX request to the radar_chart route
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/radar_chart', true);
        xhr.setRequestHeader('Content-Type', 'application/json');  // Use JSON content type
        xhr.setRequestHeader('X-CSRFToken', csrfToken);

        xhr.onload = function() {
            if (xhr.status === 200) {
                // Assuming you have a div with id 'chartContainer' to display the chart
                document.getElementById('chartContainer').innerHTML = xhr.responseText;
            } else {
                console.error('Error:', xhr.statusText);
            }
        };

        // Send selected player names and CSRF token as JSON
        var data = JSON.stringify({
            'player1_name': player1Name,
            'player2_name': player2Name,
        });

        xhr.send(data);
    };
});

document.addEventListener("DOMContentLoaded", function () {
    if (typeof(mpld3) !== "undefined" && mpld3._mpld3IsLoaded) {
        // Your existing mpld3 code
        mpld3.draw_figure("chartContainer", JSON.parse('{{ chart_html | tojson | safe }}'));
    } else {
        console.warn("mpld3 is not loaded!");
    }
});

$(document).ready(function () {
    // Toggle image size when clicking on the image
    $("#chartImage").on("click", function () {
        $(this).toggleClass("enlarged");
    });
});