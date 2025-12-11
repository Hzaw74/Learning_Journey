// Global variables
var currentImageIndex = 0;
var roomImages = [];
var currentRoomId = '';

// Load room details when page loads
function loadPage() {
    var roomImage = document.getElementById('room-img');

    if (roomImage) {
        // Get room id from URL
        var url = window.location.search;
        var params = url.split('=');
        currentRoomId = params[1];

        loadRoomDetails(currentRoomId);
        displayRoomImage();
    }
}

// Load room information based on room id
function loadRoomDetails(roomId) {
    if (roomId == 'deluxe') {
        document.getElementById('room-title').innerHTML = 'Deluxe Room';
        document.getElementById('room-price').innerHTML = '$250 per night';
        document.getElementById('room-description').innerHTML = 'A comfortable room with a king bed, city view, and modern amenities.';
        document.getElementById('room-amenities').innerHTML = '<li>40 m²</li><li>King Bed</li><li>City View</li><li>Free Wi-Fi</li>';

        roomImages[0] = 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[1] = 'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[2] = 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
    }
    else if (roomId == 'suite') {
        document.getElementById('room-title').innerHTML = 'Executive Suite';
        document.getElementById('room-price').innerHTML = '$450 per night';
        document.getElementById('room-description').innerHTML = 'Spacious suite with separate living area and premium amenities.';
        document.getElementById('room-amenities').innerHTML = '<li>65 m²</li><li>King Bed</li><li>Ocean View</li><li>Work Desk</li>';

        roomImages[0] = 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[1] = 'https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[2] = 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
    }
    else if (roomId == 'penthouse') {
        document.getElementById('room-title').innerHTML = 'Presidential Penthouse';
        document.getElementById('room-price').innerHTML = '$1200 per night';
        document.getElementById('room-description').innerHTML = 'Our most luxurious room with panoramic views and butler service.';
        document.getElementById('room-amenities').innerHTML = '<li>150 m²</li><li>2 Bedrooms</li><li>Panoramic View</li><li>Butler Service</li>';

        roomImages[0] = 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[1] = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
        roomImages[2] = 'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
    }
}

// Display the room image
function displayRoomImage() {
    var roomImage = document.getElementById('room-img');
    roomImage.src = roomImages[currentImageIndex];
}

// Show next image
function nextImage() {
    currentImageIndex = currentImageIndex + 1;
    if (currentImageIndex == 3) {
        currentImageIndex = 0;
    }
    displayRoomImage();
}

// Show previous image
function prevImage() {
    currentImageIndex = currentImageIndex - 1;
    if (currentImageIndex < 0) {
        currentImageIndex = 2;
    }
    displayRoomImage();
}

// Run when page loads
window.onload = loadPage;