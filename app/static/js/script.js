document.addEventListener('DOMContentLoaded', () => {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    // PDF Elements
    const pdfFrame = document.getElementById('pdfFrame');
    const pdfEmptyState = document.getElementById('pdfEmptyState');
    const closePdfBtn = document.getElementById('closePdfBtn');

    // Queue Elements
    const fileQueueContainer = document.getElementById('fileQueueContainer');
    const fileQueue = document.getElementById('fileQueue');
    const addMoreFilesBtn = document.getElementById('addMoreFilesBtn');

    const resultsContent = document.getElementById('resultsContent');
    const loader = document.getElementById('loader');
    const jsonViewer = document.getElementById('jsonViewer');
    const jsonCode = document.getElementById('jsonCode');
    const emptyState = document.querySelector('.empty-state');
    const processingTime = document.getElementById('processingTime');
    const downloadBtn = document.getElementById('downloadBtn');

    // State
    let filesData = []; // Array of { id, file, status, result, duration }
    let isProcessing = false;
    let activeFileId = null;

    // Drag & Drop
    uploadZone.addEventListener('click', () => fileInput.click());
    addMoreFilesBtn.addEventListener('click', () => fileInput.click());

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
            handleFiles(Array.from(e.dataTransfer.files));
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFiles(Array.from(e.target.files));
        }
        // Reset input to allow same files to be selected again if needed
        fileInput.value = '';
    });

    closePdfBtn.addEventListener('click', () => {
        // Deselect current file -> show empty state
        activeFileId = null;
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));

        pdfFrame.src = '';
        pdfFrame.classList.add('hidden');
        pdfEmptyState.classList.remove('hidden');

        // Clear results
        resetResultsUI();
    });

    downloadBtn.addEventListener('click', () => {
        const fileData = filesData.find(f => f.id === activeFileId);
        if (!fileData || !fileData.result) return;

        const dataStr = JSON.stringify(fileData.result, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `extraction_${fileData.file.name.replace('.pdf', '')}_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    function handleFiles(newFiles) {
        const pdfFiles = newFiles.filter(file => file.type === 'application/pdf');

        if (pdfFiles.length === 0) {
            alert('Please upload PDF files only.');
            return;
        }

        // Add to queue
        pdfFiles.forEach(file => {
            const id = Date.now() + Math.random().toString(36).substr(2, 9);
            filesData.push({
                id,
                file,
                status: 'pending', // pending, processing, done, error
                result: null,
                duration: null,
                error: null
            });
            renderFileItem(id);
        });

        processQueue();
    }

    function renderFileItem(id) {
        const fileData = filesData.find(f => f.id === id);
        if (!fileData) return;

        const li = document.createElement('li');
        li.className = 'file-item';
        li.dataset.id = id;
        li.innerHTML = `
            <div class="file-info">
                <span class="file-name">${fileData.file.name}</span>
                <span class="file-status status-pending">Pending</span>
            </div>
            <span class="material-symbols-outlined">chevron_right</span>
        `;

        li.addEventListener('click', () => activateFile(id));
        fileQueue.appendChild(li);
    }

    function updateFileItemUI(id) {
        const fileData = filesData.find(f => f.id === id);
        const li = fileQueue.querySelector(`.file-item[data-id="${id}"]`);
        if (!li || !fileData) return;

        const statusSpan = li.querySelector('.file-status');
        statusSpan.className = `file-status status-${fileData.status}`;

        let statusText = 'Pending';
        if (fileData.status === 'processing') statusText = 'Processing...';
        else if (fileData.status === 'done') statusText = 'Success';
        else if (fileData.status === 'error') statusText = 'Failed';

        statusSpan.textContent = statusText;
    }

    function activateFile(id) {
        activeFileId = id;
        const fileData = filesData.find(f => f.id === id);

        // Highlight in list
        document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
        const li = fileQueue.querySelector(`.file-item[data-id="${id}"]`);
        if (li) li.classList.add('active');

        // Show PDF
        const fileURL = URL.createObjectURL(fileData.file);
        pdfFrame.src = fileURL;
        pdfFrame.classList.remove('hidden');
        pdfEmptyState.classList.add('hidden');

        // Show Results area
        emptyState.classList.add('hidden');

        if (fileData.status === 'processing') {
            loader.classList.remove('hidden');
            jsonViewer.classList.add('hidden');
            downloadBtn.classList.add('hidden');
            processingTime.textContent = 'Processing...';
        } else if (fileData.status === 'done') {
            loader.classList.add('hidden');
            jsonViewer.classList.remove('hidden');
            jsonCode.textContent = JSON.stringify(fileData.result, null, 2);
            jsonViewer.style.color = '#1e293b';
            downloadBtn.classList.remove('hidden');
            processingTime.textContent = `Processed in ${fileData.duration}s`;
        } else if (fileData.status === 'error') {
            loader.classList.add('hidden');
            jsonViewer.classList.remove('hidden');
            jsonCode.textContent = `Error: ${fileData.error}`;
            jsonViewer.style.color = 'red';
            downloadBtn.classList.add('hidden');
            processingTime.textContent = 'Failed';
        } else {
            // Pending
            resetResultsUI(true);
            processingTime.textContent = 'Waiting to process...';
            // Show empty state with waiting text maybe? Or just keep empty.
            // Actually let's just show loader for pending if we want immediate feedback
            // But for queue, it stays in list until processed.
            // If user clicks it, we show "Waiting"
            loader.classList.add('hidden');
            emptyState.querySelector('p').textContent = 'Waiting to process...';
            emptyState.classList.remove('hidden');
        }
    }

    function resetResultsUI(keepEmptyHidden = false) {
        loader.classList.add('hidden');
        jsonViewer.classList.add('hidden');
        downloadBtn.classList.add('hidden');
        processingTime.textContent = '';
        jsonCode.textContent = '';
        if (!keepEmptyHidden) {
            emptyState.querySelector('p').textContent = 'Select a file to extract data';
            emptyState.classList.remove('hidden');
        }
    }

    async function processQueue() {
        if (isProcessing) return;

        const nextFile = filesData.find(f => f.status === 'pending');
        if (!nextFile) return;

        isProcessing = true;
        nextFile.status = 'processing';
        updateFileItemUI(nextFile.id);

        // If this is the active file, update the main view too
        if (activeFileId === nextFile.id) {
            activateFile(nextFile.id);
        } else if (!activeFileId) {
            // Auto open first file
            activateFile(nextFile.id);
        }

        const formData = new FormData();
        formData.append('file', nextFile.file);
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

            nextFile.status = 'done';
            nextFile.result = data;
            nextFile.duration = ((Date.now() - startTime) / 1000).toFixed(2);

        } catch (error) {
            nextFile.status = 'error';
            nextFile.error = error.message;
        } finally {
            updateFileItemUI(nextFile.id);
            if (activeFileId === nextFile.id) {
                activateFile(nextFile.id);
            }

            isProcessing = false;
            // Process next
            processQueue();
        }
    }
});
