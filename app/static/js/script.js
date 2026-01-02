document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const pdfViewerContainer = document.getElementById('pdfViewerContainer');
    const pdfFrame = document.getElementById('pdfFrame');
    const closePdfBtn = document.getElementById('closePdfBtn');

    const resultsContent = document.getElementById('resultsContent');
    const loader = document.getElementById('loader');
    const jsonViewer = document.getElementById('jsonViewer');
    const jsonCode = document.getElementById('jsonCode');
    const emptyState = document.querySelector('.empty-state');
    const processingTime = document.getElementById('processingTime');
    const downloadBtn = document.getElementById('downloadBtn');

    let currentJsonData = null;

    // Drag & Drop
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });

    closePdfBtn.addEventListener('click', () => {
        resetUI();
    });

    downloadBtn.addEventListener('click', () => {
        if (!currentJsonData) return;

        const dataStr = JSON.stringify(currentJsonData, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `extraction_result_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    function handleFile(file) {
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file.');
            return;
        }

        // Show PDF
        const fileURL = URL.createObjectURL(file);
        pdfFrame.src = fileURL;

        uploadZone.classList.add('hidden');
        pdfViewerContainer.classList.remove('hidden');

        // Start Processing
        processDocument(file);
    }

    async function processDocument(file) {
        // UI State: Loading
        emptyState.classList.add('hidden');
        jsonViewer.classList.add('hidden');
        loader.classList.remove('hidden');
        processingTime.textContent = '';
        jsonCode.textContent = '';

        const formData = new FormData();
        formData.append('file', file);

        const startTime = Date.now();

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Upload failed');
            }

            const data = await response.json();

            // Format JSON
            currentJsonData = data;
            jsonCode.textContent = JSON.stringify(data, null, 2);
            jsonViewer.classList.remove('hidden');
            downloadBtn.classList.remove('hidden');

            const duration = ((Date.now() - startTime) / 1000).toFixed(2);
            processingTime.textContent = `Processed in ${duration}s`;

        } catch (error) {
            jsonCode.textContent = `Error: ${error.message}`;
            jsonViewer.classList.remove('hidden');
            jsonViewer.style.color = 'red';
        } finally {
            loader.classList.add('hidden');
        }
    }

    function resetUI() {
        uploadZone.classList.remove('hidden');
        pdfViewerContainer.classList.add('hidden');
        pdfFrame.src = '';
        fileInput.value = '';

        emptyState.classList.remove('hidden');
        jsonViewer.classList.add('hidden');
        downloadBtn.classList.add('hidden');
        processingTime.textContent = '';
        currentJsonData = null;
    }
});
