// JavaScript code
const form = document.querySelector('form');
const inputFile = document.getElementById('file-upload');
const submitBtn = document.getElementById('submit-btn');
const loadingSpinner = document.getElementById('loading-spinner');
const predictionText = document.getElementById('prediction-text');
const originalImg = document.getElementById('original-img');
const grayscaleImg = document.getElementById('grayscale-img');
const edgedImg = document.getElementById('edged-img');
const contoursImg = document.getElementById('contours-img');
const topContoursImg = document.getElementById('top-contours-img');
const detectedPlateImg = document.getElementById('detected-plate-img');
const croppedImg = document.getElementById('cropped-img');

submitBtn.addEventListener('click', async (e) => {
    e.preventDefault();
    const file = inputFile.files[0];
    if (!file) return;
    loadingSpinner.classList.remove('hidden');
    submitBtn.disabled = true;
    const formData = new FormData();
    formData.append('image', file);
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        predictionText.textContent = `Prediction: ${data.prediction}`;
        originalImg.src = data.original_image;
        grayscaleImg.src = data.grayscale_image;
        edgedImg.src = data.edged_image;
        contoursImg.src = data.contours_image;
        topContoursImg.src = data.top_contours_image;
        detectedPlateImg.src = data.detected_plate_image;
        croppedImg.src = data.cropped_image;
        predictionText.classList.remove('hidden');
        imageContainer.classList.remove('hidden');
    } catch (error) {
        console.log(error);
        alert('Failed to upload image');
    } finally {
        loadingSpinner.classList.add('hidden');
        submitBtn.disabled = false;
        inputFile.value = '';
    }
});
