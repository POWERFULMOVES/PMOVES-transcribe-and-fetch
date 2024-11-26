// Global variable to store the current folders
let currentFolders = {};

// Function to fetch and display output folders
async function displayOutputFolders() {
    try {
        const response = await fetch('/output-folders/');
        currentFolders = await response.json();
        const folderList = document.getElementById('folder-list');
        folderList.innerHTML = '<h3>Output Folders:</h3>';
        for (const [key, value] of Object.entries(currentFolders)) {
            folderList.innerHTML += `
                <div class="folder-item">
                    <strong>${key}:</strong> 
                    <span id="folder-${key}">${value}</span>
                    <button onclick="showUpdateFolder('${key}')">Change</button>
                </div>
                <div id="update-${key}" style="display:none;">
                    <input type="text" id="input-${key}" value="${value}">
                    <button onclick="updateFolder('${key}')">Save</button>
                    <button onclick="cancelUpdate('${key}')">Cancel</button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching output folders:', error);
        showError('Failed to fetch output folders. Please try again.');
    }
}

function showUpdateFolder(key) {
    document.getElementById(`folder-${key}`).style.display = 'none';
    document.getElementById(`update-${key}`).style.display = 'block';
}

function cancelUpdate(key) {
    document.getElementById(`folder-${key}`).style.display = 'inline';
    document.getElementById(`update-${key}`).style.display = 'none';
}

async function updateFolder(key) {
    const newPath = document.getElementById(`input-${key}`).value.trim();
    if (newPath && newPath !== currentFolders[key]) {
        try {
            const response = await fetch('/update-folder/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ key: key, new_path: newPath }),
            });
            if (!response.ok) {
                throw new Error('Failed to update folder');
            }
            const result = await response.json();
            showSuccess(result.message);
            await displayOutputFolders();  // Refresh the folder list
        } catch (error) {
            console.error('Error updating folder:', error);
            showError('Failed to update folder. Please try again.');
        }
    }
    cancelUpdate(key);
}

// Function to display the completed transcript
function showCompletedTranscript(result) {
    const completedTranscriptElement = document.getElementById('completed-transcript');
    completedTranscriptElement.innerText = result;
}

// Function to display error messages
function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Function to display success messages
function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 5000);
}

// Variable to store the EventSource instance
let eventSource;

// Function to start the transcription process
function startTranscription(youtubeUrl) {
    // Close existing event source if any
    if (eventSource) {
        eventSource.close();
    }

    // Start new transcription
    fetch('/process-video/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            youtube_video_url: youtubeUrl,
            obsidian_dir: currentFolders.obsidian,
            output_folder: currentFolders.main
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Transcription started:', data);
        // Start listening for updates
        startEventSource();
    })
    .catch(error => {
        console.error('Error starting transcription:', error);
        showError('Failed to start transcription. Please try again.');
    });
}

function startEventSource() {
    eventSource = new EventSource('/combined-updates/');
    const statusUpdatesElement = document.getElementById('status-updates');
    const transcriptionUpdatesElement = document.getElementById('transcription-updates');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data.type === 'status') {
            statusUpdatesElement.innerHTML += data.content + '<br>';
        } else if (data.type === 'transcription') {
            // Only append the text from the content object
            transcriptionUpdatesElement.innerHTML += data.content.text + ' ';
        } else if (data.type === 'transcription_complete') {
            transcriptionUpdatesElement.innerHTML += '<br><strong>Transcription complete.</strong>';
            eventSource.close();
            getFinalResult();
        } else if (data.type === 'keepalive') {
            // Ignore keepalive messages
        } else {
            console.warn('Unknown update type:', data.type);
        }
    };

    eventSource.onerror = function(error) {
        console.error('EventSource failed:', error);
        eventSource.close();
        showError('Lost connection to the server. Please try again.');
    };
}

// Function to get the final transcription result
function getFinalResult() {
    fetch('/get-final-result')
        .then(response => response.json())
        .then(result => {
            showCompletedTranscript(result);
            showSuccess('Transcription completed successfully!');
        })
        .catch(error => {
            console.error('Error getting final result:', error);
            showError('Failed to get final result. Please check the server logs.');
        });
}

// Set up event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    displayOutputFolders();
    
    // Set up the form submission
    const form = document.getElementById('transcription-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const youtubeUrl = document.getElementById('youtube-url').value;
        startTranscription(youtubeUrl);
    });
});

// Function to display live transcription updates
function showLiveTranscription(text) {
    const liveTranscriptionElement = document.getElementById('live-transcription');
    liveTranscriptionElement.innerText += text;
}