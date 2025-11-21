// Camera utility functions for PicMe
// Handles webcam access and photo capture

class CameraHandler {
    constructor() {
        this.stream = null;
        this.video = null;
    }

    async startCamera(videoElement) {
        this.video = videoElement;
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'user' },
                audio: false 
            });
            this.video.srcObject = this.stream;
            return true;
        } catch (error) {
            console.error('Camera access error:', error);
            return false;
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }

    capturePhoto(canvas) {
        if (!this.video) return null;
        const context = canvas.getContext('2d');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
    }
}

// Export for use in other scripts
window.CameraHandler = CameraHandler;
