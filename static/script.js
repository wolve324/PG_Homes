document.addEventListener('DOMContentLoaded', function () {
    // Tab functionality
    const tabs = document.querySelectorAll('.tab-link');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // Add active class to the clicked tab and corresponding content
            const targetId = tab.getAttribute('data-tab');
            tab.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Initialize Masonry layout
    const grid = document.querySelector('.grid');
    if (grid) {
        const msnry = new Masonry(grid, {
            itemSelector: '.grid-item',
            columnWidth: '.grid-item',
            percentPosition: true,
        });
    }
});

// Function to show/hide sections based on selected area
function operation() {
    const area = document.getElementById('area').value;
    const sections = [
        'Sect_1',
        'Sect_2',
        'Sect_3',
        'Sect_4',
        'Sect_8',
        'Sect_19',
        'Sect_20',
    ];

    // Hide all sections initially
    sections.forEach(section => {
        document.getElementById(section).classList.add('hidden');
    });

    // Show the selected section if it starts with "Sect"
    if (area.startsWith('Sect')) {
        const targetSection = area.replace(' ', '_');
        document.getElementById(targetSection).classList.remove('hidden');
    }
}

// Function to update the selected property value
function updateProperty(selectElement) {
    const selectedProperty = selectElement.value;
    document.getElementById('Property_selected').value = selectedProperty;
}