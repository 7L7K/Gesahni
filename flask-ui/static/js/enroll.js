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
}

export { initEnrollment };
