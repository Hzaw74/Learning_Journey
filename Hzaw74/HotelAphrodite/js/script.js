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

        roomImages[0] = 'images/visualsofdana-T5pL6ciEn-I-unsplash.jpg';
        roomImages[1] = 'images/kenny-eliason-iAftdIcgpFc-unsplash.jpg';
        roomImages[2] = 'images/lotus-design-n-print-g51F6-WYzyU-unsplash.jpg';
    }
    else if (roomId == 'suite') {
        document.getElementById('room-title').innerHTML = 'Executive Suite';
        document.getElementById('room-price').innerHTML = '$450 per night';
        document.getElementById('room-description').innerHTML = 'Spacious suite with separate living area and premium amenities.';
        document.getElementById('room-amenities').innerHTML = '<li>65 m²</li><li>King Bed</li><li>Ocean View</li><li>Work Desk</li>';

        roomImages[0] = 'images/sasha-kaunas-67-sOi7mVIk-unsplash.jpg';
        roomImages[1] = 'images/lotus-design-n-print-g8tb9SXqZVQ-unsplash.jpg';
        roomImages[2] = 'images/ikhbale-4eUol_FVp3o-unsplash.jpg';
    }
    else if (roomId == 'penthouse') {
        document.getElementById('room-title').innerHTML = 'Presidential Penthouse';
        document.getElementById('room-price').innerHTML = '$1200 per night';
        document.getElementById('room-description').innerHTML = 'Our most luxurious room with panoramic views and butler service.';
        document.getElementById('room-amenities').innerHTML = '<li>150 m²</li><li>2 Bedrooms</li><li>Panoramic View</li><li>Butler Service</li>';

        roomImages[0] = 'images/point3d-commercial-imaging-ltd-oxeCZrodz78-unsplash.jpg';
        roomImages[1] = 'images/point3d-commercial-imaging-ltd-_Swg04CP0bU-unsplash.jpg';
        roomImages[2] = 'images/francesca-tosolini-qnSTxcs0EEs-unsplash.jpg';
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