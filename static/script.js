function showMessage(message, isError = false) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = isError ? 'alert alert-danger' : 'alert alert-success';
    messageDiv.innerText = message;
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 3000);
}

function editMapping(j1Field, j2Field, type) {
    document.getElementById('oldJ1Field').value = j1Field;
    document.getElementById('j1Field').value = j1Field;
    document.getElementById('j2Field').value = j2Field;
    document.getElementById('type').value = type;
    $('#editMappingModal').modal('show');
}

function showAddMappingModal() {
    $('#addMappingModal').modal('show');
}

function resolveMismatch(j1Field, j1Type) {
    document.getElementById('mismatchJ1Field').value = j1Field;
    document.getElementById('mismatchJ1Type').value = j1Type;
    $('#resolveMismatchModal').modal('show');
}

document.getElementById('editMappingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const oldJ1Field = document.getElementById('oldJ1Field').value;
    const j1Field = document.getElementById('j1Field').value;
    const j2Field = document.getElementById('j2Field').value;
    const type = document.getElementById('type').value;

    fetch('/edit_mapping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ old_j1_field: oldJ1Field, j1_field: j1Field, j2_field: j2Field, type: type }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Mapping updated successfully');
            $('#editMappingModal').modal('hide');
            location.reload();
        } else {
            showMessage('Failed to update mapping', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
});

document.getElementById('addMappingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const j1Field = document.getElementById('newJ1Field').value;
    const j2Field = document.getElementById('newJ2Field').value;
    const type = document.getElementById('newType').value;

    fetch('/add_mapping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ j1_field: j1Field, j2_field: j2Field, type: type }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Mapping added successfully');
            $('#addMappingModal').modal('hide');
            location.reload();
        } else {
            showMessage('Failed to add mapping', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
});

document.getElementById('resolveMismatchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const j1Field = document.getElementById('mismatchJ1Field').value;
    const j2Field = document.getElementById('resolveJ2Field').value;
    const type = document.getElementById('resolveType').value;

    fetch('/resolve_mismatch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ j1_field: j1Field, j2_field: j2Field, type: type }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Mismatch resolved successfully');
            $('#resolveMismatchModal').modal('hide');
            location.reload();
        } else {
            showMessage('Failed to resolve mismatch', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
});

function saveMappings() {
    fetch('/save_mapping', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Mappings saved successfully');
        } else {
            showMessage('Failed to save mappings', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
}

function generateOutput() {
    fetch('/generate_output', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Output generated successfully');
        } else {
            showMessage('Failed to generate output', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
}

function undoChanges() {
    fetch('/undo_changes', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('Changes undone successfully');
            location.reload();
        } else {
            showMessage('Failed to undo changes', true);
        }
    })
    .catch((error) => {
        showMessage('Error: ' + error, true);
    });
}

function downloadOutput() {
    window.location.href = '/download_output';
}
