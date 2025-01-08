document.getElementById('payment_details').addEventListener('submit', function() {
    document.getElementById('processing-message').style.display = 'block';
    document.getElementById('submit-button').disabled = true;
})