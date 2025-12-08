// Global variables
let currentRoomId = '';
let currentImageIndex = 0;
let roomImages = [];

// Called when the body loads
function loadPage() {
    console.log('Page loaded');

    // Check if we are on the room details page by looking for the room-img
    let roomImage = document.getElementById('room-img');

    if (roomImage) {
        // Get URL parameter manually
        const urlParams = new URLSearchParams(window.location.search);
        let id = urlParams.get('id');
        console.log('Room ID:', id);
        currentRoomId = id;

        // Giant IF/ELSE block instead of Object
        if (id == 'deluxe') {
            document.getElementById('room-title').innerHTML = 'Deluxe Room';
            document.getElementById('room-price').innerHTML = '$250 / night';
            document.getElementById('room-description').innerHTML = 'A perfect blend of comfort and style, featuring a king-sized bed, city views, and a marble bathroom with a rain shower.';

            // Manually building the list string
            let amenitiesHtml = '';
            amenitiesHtml = amenitiesHtml + '<li>- 40 m²</li>';
            amenitiesHtml = amenitiesHtml + '<li>- King Bed</li>';
            amenitiesHtml = amenitiesHtml + '<li>- City View</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Free Wi-Fi</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Smart TV</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Mini Bar</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            // Arrays for images
            roomImages[0] = 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'suite') {
            document.getElementById('room-title').innerHTML = 'Executive Suite';
            document.getElementById('room-price').innerHTML = '$450 / night';
            document.getElementById('room-description').innerHTML = 'Elevate your stay with a separate living area, executive lounge access, and premium bath amenities.';

            let amenitiesHtml = '';
            amenitiesHtml = amenitiesHtml + '<li>- 65 m²</li>';
            amenitiesHtml = amenitiesHtml + '<li>- King Bed</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Ocean View</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Lounge Access</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Bathtub</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Work Desk</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'family') {
            document.getElementById('room-title').innerHTML = 'Family Studio';
            document.getElementById('room-price').innerHTML = '$350 / night';
            document.getElementById('room-description').innerHTML = 'Spacious accommodation designed for families, featuring two queen beds and a kitchenette.';

            let amenitiesHtml = '';
            amenitiesHtml = amenitiesHtml + '<li>- 55 m²</li>';
            amenitiesHtml = amenitiesHtml + '<li>- 2 Queen Beds</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Garden View</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Kitchenette</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Gaming Console</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Kids Area</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1616486338812-3a47728331a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'villa') {
            document.getElementById('room-title').innerHTML = 'Ocean View Villa';
            document.getElementById('room-price').innerHTML = '$800 / night';
            document.getElementById('room-description').innerHTML = 'A private sanctuary with direct beach access, private pool, and stunning sunset views.';

            let amenitiesHtml = '';
            amenitiesHtml = amenitiesHtml + '<li>- 120 m²</li>';
            amenitiesHtml = amenitiesHtml + '<li>- King Bed</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Ocean Front</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Private Pool</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Outdoor Shower</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Hammock</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1473186578169-21484728384d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'penthouse') {
            document.getElementById('room-title').innerHTML = 'Presidential Penthouse';
            document.getElementById('room-price').innerHTML = '$1,200 / night';
            document.getElementById('room-description').innerHTML = 'Unmatched luxury on the top floor. Features a private terrace, jacuzzi, dining area, and 24-hour butler service.';

            let amenitiesHtml = '';
            amenitiesHtml = amenitiesHtml + '<li>- 150 m²</li>';
            amenitiesHtml = amenitiesHtml + '<li>- 2 Bedrooms</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Panoramic View</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Private Terrace</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Jacuzzi</li>';
            amenitiesHtml = amenitiesHtml + '<li>- Butler Service</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else {
            document.querySelector('.room-details-section').innerHTML = '<h2>Room not found</h2>';
        }

        // Set initial image
        document.getElementById('room-img').src = roomImages[0];
    }
}

// Global functions for buttons to call directly
function nextImage() {
    currentImageIndex = currentImageIndex + 1;

    if (currentImageIndex == 3) {
        currentImageIndex = 0;
    }

    document.getElementById('room-img').src = roomImages[currentImageIndex];
    console.log('Next image: ' + currentImageIndex);
}

function prevImage() {
    currentImageIndex = currentImageIndex - 1;

    if (currentImageIndex < 0) {
        currentImageIndex = 2;
    }

    document.getElementById('room-img').src = roomImages[currentImageIndex];
    console.log('Prev image: ' + currentImageIndex);
}

// Run loadPage when window is ready
window.onload = loadPage;
