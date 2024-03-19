document.addEventListener('DOMContentLoaded', function() {
    const predictBtn = document.getElementById('predict-btn');
    const inputData = document.getElementById('input-data');
    const predictionResult = document.getElementById('prediction-result');

    predictBtn.addEventListener('click', function() {
        const data = inputData.value.trim();
        if (data === '') {
            predictionResult.textContent = 'Please enter data.';
            return;
        }

        fetch('http://localhost:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: data })
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
