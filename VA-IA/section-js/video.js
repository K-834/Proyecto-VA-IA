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
