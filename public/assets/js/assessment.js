// newsviz.js

document.addEventListener('DOMContentLoaded', function() {
    // Array to hold RSS feed URLs
    let rssFeedsArray = [];

    // Elements
    const rssForm = document.getElementById('rssForm');
    const rssInput = document.getElementById('rssInput');
    const addFeedBtn = document.getElementById('addFeedBtn');
    const feedList = document.getElementById('feedList');

    // Add feed button event listener
    addFeedBtn.addEventListener('click', function() {
        const rssUrl = rssInput.value.trim();
        if (rssUrl) {
            addFeedToList(rssUrl);
            rssInput.value = '';
        }
    });

    // Function to add feed to the list
    function addFeedToList(rssUrl) {
        // Check if the URL is already in the list
        if (rssFeedsArray.includes(rssUrl)) {
            alert('This RSS feed URL is already added.');
            return;
        }

        // Add to array
        rssFeedsArray.push(rssUrl);

        // Create feed item
        const feedItem = document.createElement('div');
        feedItem.className = 'feed-item animate__animated animate__fadeInUp';
        feedItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center p-3 bg-light rounded mb-2">
                <div class="feed-url text-break">${rssUrl}</div>
                <button class="btn btn-danger btn-sm remove-feed-btn"><i class="fas fa-trash"></i></button>
            </div>
        `;
        // Append to feed list
        feedList.appendChild(feedItem);

        // Remove feed event
        const removeBtn = feedItem.querySelector('.remove-feed-btn');
        removeBtn.addEventListener('click', function() {
            feedList.removeChild(feedItem);
            rssFeedsArray = rssFeedsArray.filter(url => url !== rssUrl);
        });
    }

    // Form submission event
    rssForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        if (rssFeedsArray.length === 0) {
            alert('Please add at least one RSS feed URL.');
            return;
        }

        document.getElementById('loadingOverlay').style.display = 'block';

        sendRssFeedsToApi();
    });

    // Function to send RSS feed URLs to the Python API
    function sendRssFeedsToApi() {
        fetch('http://127.0.0.1:5000/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Connection': 'close', // Add Connection header
                'Host': '127.0.0.1:5000' // Add Host header
            },
            body: JSON.stringify({ rssFeeds: rssFeedsArray }) // Properly structure the JSON data
        })
        .then(response => {
            document.getElementById('loadingOverlay').style.display = 'none';
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Success:', data);
            // Redirect or perform any action after receiving a response
            document.getElementById('loadingOverlay').style.display = 'none';
            localStorage.setItem('apiData', JSON.stringify(data));
            window.location.href = 'news.html'; // Change to your desired page

        })
        .catch((error) => {
            document.getElementById('loadingOverlay').style.display = 'none';
            console.error('Error:', error);
            alert('An error occurred while sending RSS feeds to the server.');
        });
    }
});