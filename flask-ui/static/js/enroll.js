// Consent check before running anything else
async function initEnrollment() {
    if (!localStorage.getItem('consent_given')) {
        window.location.href = '/consent';
        return;
    }
    try {
        await fetch('/enroll/init', { method: 'POST' });
    } catch (err) {
        console.error('init failed', err);
    }
    // Continue with rest of UI setup
    initEnrollmentUI();
}

function initEnrollmentUI() {
    const UI = {
        step: 'voice',
        voiceBlob: null,
        faces: [],
        userId: CONFIG.user_id
    };

    const uppy = new Uppy.Core();
    uppy.use(Uppy.Tus, { endpoint: CONFIG.TUSD_URL });

    const voiceStep = document.getElementById('voice-step');
    const faceStep = document.getElementById('face-step');
    const statusStep = document.getElementById('status-step');

    const micBtn = document.getElementById('mic-btn');
    const countdownEl = document.getElementById('countdown');
    const voiceFallback = document.getElementById('voice-fallback');
    const voiceFileInput = document.getElementById('voice-file');
    const voiceUploadBtn = document.getElementById('voice-upload');

    let recorder, chunks = [], countdownInt;

    function startCountdown(sec, onEnd) {
        countdownEl.textContent = sec;
        countdownInt = setInterval(() => {
            sec--;
            countdownEl.textContent = sec;
            if (sec <= 0) {
                clearInterval(countdownInt);
                onEnd();
            }
        }, 1000);
    }

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            recorder = new MediaRecorder(stream);
            chunks = [];
            recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
            recorder.onstop = () => {
                UI.voiceBlob = new Blob(chunks, { type: 'audio/wav' });
                submitVoice(UI.voiceBlob);
            };
            recorder.start();
            startCountdown(10, () => recorder.stop());
        }).catch(() => {
            voiceFallback.classList.remove('hidden');
        });
    }

    function submitVoice(blob) {
        const form = new FormData();
        form.append('file', blob, 'voice.wav');
        fetch(`/enroll/voice/${UI.userId}`, { method: 'POST', body: form })
            .then(() => showFaceStep())
            .catch(err => console.error(err));
    }

    micBtn.addEventListener('mousedown', startRecording);
    voiceUploadBtn.addEventListener('click', () => {
        const f = voiceFileInput.files[0];
        if (f) submitVoice(f);
    });

    function showFaceStep() {
        UI.step = 'face';
        voiceStep.classList.add('hidden');
        faceStep.classList.remove('hidden');
        initCamera();
    }

    const videoEl = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const facePrompt = document.getElementById('face-prompt');
    const captureBtn = document.getElementById('capture-btn');
    const faceFallback = document.getElementById('face-fallback');
    const faceUploadBtn = document.getElementById('face-upload');
    const frontFile = document.getElementById('front-file');
    const leftFile = document.getElementById('left-file');
    const rightFile = document.getElementById('right-file');

    const prompts = ['front', 'left', 'right'];
    let current = 0;
    let camStream;

    function initCamera() {
        navigator.mediaDevices.getUserMedia({ video: true }).then(s => {
            camStream = s;
            videoEl.srcObject = s;
            facePrompt.textContent = `Look ${prompts[current]}`;
        }).catch(() => {
            faceFallback.classList.remove('hidden');
        });
    }

    captureBtn.addEventListener('click', captureFrame);

    function captureFrame() {
        if (!camStream) return;
        canvas.getContext('2d').drawImage(videoEl, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(b => {
            UI.faces.push(b);
            if (current < prompts.length - 1) {
                current++;
                facePrompt.textContent = `Look ${prompts[current]}`;
            } else {
                submitFaces();
            }
        }, 'image/jpeg');
    }

    faceUploadBtn.addEventListener('click', () => {
        const form = new FormData();
        form.append('front', frontFile.files[0]);
        form.append('left', leftFile.files[0]);
        form.append('right', rightFile.files[0]);
        submitFaces(form);
    });

    function submitFaces(formData) {
        const form = formData || new FormData();
        if (!formData) {
            form.append('front', UI.faces[0], 'front.jpg');
            form.append('left', UI.faces[1], 'left.jpg');
            form.append('right', UI.faces[2], 'right.jpg');
        }
        fetch(`/enroll/face/${UI.userId}`, { method: 'POST', body: form })
            .then(() => showStatus())
            .catch(err => console.error(err));
    }

    function showStatus() {
        UI.step = 'status';
        faceStep.classList.add('hidden');
        statusStep.classList.remove('hidden');
        pollStatus();
    }

    function pollStatus() {
        const int = setInterval(() => {
            fetch(`/enroll/status/${UI.userId}`)
                .then(r => r.json())
                .then(d => {
                    if (d.done || d.status === 'complete') {
                        clearInterval(int);
                        const audio = new Audio('/static/welcome.mp3');
                        audio.play();
                        window.location.href = '/chat';
                    }
                });
        }, 3000);
    }
}

// Only export the consent-checked initializer
export { initEnrollment };
