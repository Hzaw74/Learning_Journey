var currentRoomId = '';
var currentImageIndex = 0;
var roomImages = [];

function loadPage() {
    console.log('Page loaded');

    var roomImage = document.getElementById('room-img');

    if (roomImage) {

        var url = window.location.search;
        var params = url.split('=');
        var id = params[1];

        console.log('Room ID:', id);
        currentRoomId = id;

        if (id == 'deluxe') {
            document.getElementById('room-title').innerHTML = 'Deluxe Room';
            document.getElementById('room-price').innerHTML = '$250 / night';
            document.getElementById('room-description').innerHTML = 'A perfect blend of comfort and style, featuring a king-sized bed, city views, and a marble bathroom with a rain shower.';

            var amenitiesHtml = '<li>- 40 m²</li><li>- King Bed</li><li>- City View</li><li>- Free Wi-Fi</li><li>- Smart TV</li><li>- Mini Bar</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'suite') {
            document.getElementById('room-title').innerHTML = 'Executive Suite';
            document.getElementById('room-price').innerHTML = '$450 / night';
            document.getElementById('room-description').innerHTML = 'Elevate your stay with a separate living area, executive lounge access, and premium bath amenities.';

            var amenitiesHtml = '<li>- 65 m²</li><li>- King Bed</li><li>- Ocean View</li><li>- Lounge Access</li><li>- Bathtub</li><li>- Work Desk</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'family') {
            document.getElementById('room-title').innerHTML = 'Family Studio';
            document.getElementById('room-price').innerHTML = '$350 / night';
            document.getElementById('room-description').innerHTML = 'Spacious accommodation designed for families, featuring two queen beds and a kitchenette.';

            var amenitiesHtml = '<li>- 55 m²</li><li>- 2 Queen Beds</li><li>- Garden View</li><li>- Kitchenette</li><li>- Gaming Console</li><li>- Kids Area</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'villa') {
            document.getElementById('room-title').innerHTML = 'Ocean View Villa';
            document.getElementById('room-price').innerHTML = '$800 / night';
            document.getElementById('room-description').innerHTML = 'A private sanctuary with direct beach access, private pool, and stunning sunset views.';

            var amenitiesHtml = '<li>- 120 m²</li><li>- King Bed</li><li>- Ocean Front</li><li>- Private Pool</li><li>- Outdoor Shower</li><li>- Hammock</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else if (id == 'penthouse') {
            document.getElementById('room-title').innerHTML = 'Presidential Penthouse';
            document.getElementById('room-price').innerHTML = '$1,200 / night';
            document.getElementById('room-description').innerHTML = 'Unmatched luxury on the top floor. Features a private terrace, jacuzzi, dining area, and 24-hour butler service.';

            var amenitiesHtml = '<li>- 150 m²</li><li>- 2 Bedrooms</li><li>- Panoramic View</li><li>- Private Terrace</li><li>- Jacuzzi</li><li>- Butler Service</li>';
            document.getElementById('room-amenities').innerHTML = amenitiesHtml;

            roomImages[0] = 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[1] = 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
            roomImages[2] = 'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';

        } else {
            document.getElementsByClassName('room-details-section')[0].innerHTML = '<h2>Room not found</h2>';
        }

        document.getElementById('room-img').src = roomImages[0];
    }
}

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

window.onload = loadPage;
