// Wait for document to load
document.addEventListener('DOMContentLoaded', function () {
    console.log('Page loaded');

    // Room Data
    // Storing details for each room type
    let roomData = {
        'deluxe': {
            title: 'Deluxe Room',
            price: '$250',
            description: 'A perfect blend of comfort and style, featuring a king-sized bed, city views, and a marble bathroom with a rain shower.',
            amenities: ['40 m²', 'King Bed', 'City View', 'Free Wi-Fi', 'Smart TV', 'Mini Bar'],
            images: [
                'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'suite': {
            title: 'Executive Suite',
            price: '$450',
            description: 'Elevate your stay with a separate living area, executive lounge access, and premium bath amenities.',
            amenities: ['65 m²', 'King Bed', 'Ocean View', 'Lounge Access', 'Bathtub', 'Work Desk'],
            images: [
                'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'family': {
            title: 'Family Studio',
            price: '$350',
            description: 'Spacious accommodation designed for families, featuring two queen beds and a kitchenette.',
            amenities: ['55 m²', '2 Queen Beds', 'Garden View', 'Kitchenette', 'Gaming Console', 'Kids Area'],
            images: [
                'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1616486338812-3a47728331a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'villa': {
            title: 'Ocean View Villa',
            price: '$800',
            description: 'A private sanctuary with direct beach access, private pool, and stunning sunset views.',
            amenities: ['120 m²', 'King Bed', 'Ocean Front', 'Private Pool', 'Outdoor Shower', 'Hammock'],
            images: [
                'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1473186578169-21484728384d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'penthouse': {
            title: 'Presidential Penthouse',
            price: '$1,200',
            description: 'Unmatched luxury on the top floor. Features a private terrace, jacuzzi, dining area, and 24-hour butler service.',
            amenities: ['150 m²', '2 Bedrooms', 'Panoramic View', 'Private Terrace', 'Jacuzzi', 'Butler Service'],
            images: [
                'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        }
    };

    // Only run on the details page
    let roomImage = document.getElementById('room-img');

    if (roomImage) {
        // Get URL parameter
        let urlParams = new URLSearchParams(window.location.search);
        let id = urlParams.get('id');
        console.log('Room ID:', id);

        let room = roomData[id];

        if (room) {
            // Fill text
            document.getElementById('room-title').textContent = room.title;
            document.getElementById('room-price').textContent = room.price + ' / night';
            document.getElementById('room-description').textContent = room.description;

            // Fill amenities list
            let list = document.getElementById('room-amenities');
            for (let i = 0; i < room.amenities.length; i++) {
                let item = document.createElement('li');
                item.textContent = '- ' + room.amenities[i]; // Simple string
                list.appendChild(item);
            }

            // Image Switching Logic
            let currentImageIndex = 0;

            // Show first image
            roomImage.src = room.images[0];

            // Button clicks
            document.getElementById('next-btn').addEventListener('click', function () {
                // Go to next index
                currentImageIndex++;
                // If at end, go back to start
                if (currentImageIndex >= room.images.length) {
                    currentImageIndex = 0;
                }
                // Update image
                roomImage.src = room.images[currentImageIndex];
                console.log('Show image ' + currentImageIndex);
            });

            document.getElementById('prev-btn').addEventListener('click', function () {
                // Go to prev index
                currentImageIndex--;
                // If below 0, go to end
                if (currentImageIndex < 0) {
                    currentImageIndex = room.images.length - 1;
                }
                // Update image
                roomImage.src = room.images[currentImageIndex];
                console.log('Show image ' + currentImageIndex);
            });

        } else {
            console.log('Invalid room');
            document.querySelector('.room-details-section').innerHTML = '<h2>Room not found</h2>';
        }
    }

});
