document.addEventListener('DOMContentLoaded', function() {
    const cameras = document.querySelectorAll('.camera');
    const videoModal = new bootstrap.Modal(document.getElementById('videoModal'));
    const videoPlayer = document.getElementById('videoPlayer');
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    let currentCameraIndex = 0;

    const videoSources = [
        '/img/video/jaja.mp4',
    ];

    function openVideoModal(index) {
        currentCameraIndex = index;
        videoPlayer.src = videoSources[index];
        videoPlayer.load();
        videoModal.show();
    }

    cameras.forEach((camera, index) => {
        camera.addEventListener('click', () => {
            openVideoModal(index);
        });
    });

    prevButton.addEventListener('click', () => {
        currentCameraIndex = (currentCameraIndex - 1 + videoSources.length) % videoSources.length;
        openVideoModal(currentCameraIndex);
    });

    nextButton.addEventListener('click', () => {
        currentCameraIndex = (currentCameraIndex + 1) % videoSources.length;
        openVideoModal(currentCameraIndex);
    });
});
document.getElementById("formularioEjecutar").addEventListener("submit", function (event) {
            event.preventDefault();
            // Realizar la solicitud POST al servidor Flask
            fetch('../../ProyectoVAIA.py', {
                method: 'POST',
                body: JSON.stringify({}),
                headers: {
                    'Content-Type': 'application/json'
                }
            }).then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    return Promise.reject('Error en la solicitud');
                }
            }).then(data => {
                console.log(data);
            }).catch(error => {
                console.error(error);
            });
        });