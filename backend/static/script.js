const baseURL = window.location.origin;

document.addEventListener('DOMContentLoaded', function() {
    const predictBtn = document.getElementById('predict-btn');
    const intradayPriceInput = document.getElementById('intraday-price');
    const priceChangeInput = document.getElementById('price-change');
    const volumeInput = document.getElementById('volume');
    const predictionResult = document.getElementById('prediction-result');

    predictBtn.addEventListener('click', function() {
        const intradayPrice = parseFloat(intradayPriceInput.value.trim());
        const priceChange = parseFloat(priceChangeInput.value.trim());
        const volume = parseFloat(volumeInput.value.trim());

        // Check if any of the inputs are empty or invalid
        if (isNaN(intradayPrice) || isNaN(priceChange) || isNaN(volume)) {
            predictionResult.textContent = 'Please enter valid data for all fields.';
            return;
        }

        fetch(`${baseURL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                intraday_price: intradayPrice,
                price_change: priceChange,
                volume: volume
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.prediction) {
                predictionResult.textContent = 'Prediction: ' + data.prediction;
            } else if (data.error) {
                predictionResult.textContent = 'Error: ' + data.error;
            } else {
                predictionResult.textContent = 'Unknown error occurred.';
            }
        })
        .catch(error => {
            predictionResult.textContent = 'Error: ' + error.message;
        });
    });
});
