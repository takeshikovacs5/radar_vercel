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

// Add this script to select the FW radio button on page load
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('defender').checked = true;
    updatePlayers();  // Optional: If you want to trigger the player list update
});

function updatePlayers() {
    var selectedPosition = document.querySelector('input[name="selected_position"]:checked').value;
    var player1Select = document.getElementById('player1');
    var player2Select = document.getElementById('player2');

    // Fetch the appropriate CSV file based on the selected position
    fetchPlayers(selectedPosition)
        .then(function (players) {
            // Clear existing options
            player1Select.innerHTML = '';
            player2Select.innerHTML = '';

            // Add new options
            players.forEach(function (player) {
                var option = document.createElement('option');
                option.value = player;
                option.textContent = player;
                player1Select.appendChild(option);

                option = document.createElement('option');
                option.value = player;
                option.textContent = player;
                player2Select.appendChild(option);
            });
        });
}

function fetchPlayers(position) {
    // Use appropriate URLs for each position
    var url = '';
    if (position === 'FW') {
        url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/forwards.csv';
    } else if (position === 'MF') {
        url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/midfielders.csv';
    } else if (position === 'DF') {
        url = 'https://raw.githubusercontent.com/bariscanyeksin/csv_scatter_radar/main/defenders.csv';
    }

    // Fetch the player names from the CSV file
    return fetch(url)
        .then(function (response) {
            return response.text();
        })
        .then(function (csvData) {
            // Parse CSV data and return the list of player names
            var playerNames = csvData.split('\n').slice(1, -1).map(function (line) {
                var columns = line.trim().split(',');
                return columns[columns.length - 4];
            });
            playerNames.sort(function(a, b){return a.localeCompare(b)});

            return playerNames;
        });
}

$(document).ready(function () {
    // Intercept the form submit
    $("#chartForm").submit(function (event) {
        event.preventDefault(); // Prevent the default form submission

        // Set the selected_position value to the hidden input field
        $("#selectedPosition").val($('input[name="selected_position"]:checked').val());

        var formData = $(this).serialize(); // Serialize form data

        // Show the loading spinner
        $("#loadingSpinner").show();

        function scrollToBottom() {
            $('html, body').animate({
                scrollTop: $('#chartContainer').offset().top
            }, 1600); // You can adjust the duration (milliseconds) as needed
        }
        // Make an AJAX request to the server
        $.ajax({
            type: 'POST',
            url: '/radar_chart',
            data: formData,
            cache: false,
            success: function (data) {
                // Assuming you have a div with id 'chartContainer' to display the chart
                updateChart(data);

                // Hide the loading spinner after the chart is loaded
                $("#loadingSpinner").hide();

                scrollToBottom();
            },
            error: function (xhr, status, error) {
                console.error("AJAX request failed:", status, error);

                // Hide the loading spinner in case of an error
                $("#loadingSpinner").hide();
            }
        });
    });

    // JavaScript code to update the chart container
    function updateChart(data) {
        // Get the chart container element
        var chartContainer = $("#chartContainer");

        // Update the content of the chart container with the new chart HTML
        chartContainer.html(data);
    }
});
