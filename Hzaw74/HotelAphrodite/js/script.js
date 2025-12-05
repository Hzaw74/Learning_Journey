document.addEventListener('DOMContentLoaded', () => {
    /* ====================
       Navigation Toggle
       ==================== */
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    /* ====================
       Smooth Scrolling
       ==================== */
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    /* ====================
       Scroll Animations
       ==================== */
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(section);
    });

    /* ====================
       Room Details & Slider
       ==================== */
    const roomData = {
        'deluxe': {
            title: 'Deluxe Room',
            price: '$250',
            description: 'A perfect blend of comfort and style, featuring a king-sized bed, city views, and a marble bathroom with a rain shower. Ideal for business travelers and couples looking for a sophisticated retreat in the heart of the city.',
            amenities: ['40 m²', 'King Bed', 'City View', 'Free Wi-Fi', 'Smart TV', 'Mini Bar', 'Rain Shower', 'Coffee Maker'],
            images: [
                'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'suite': {
            title: 'Executive Suite',
            price: '$450',
            description: 'Elevate your stay with a separate living area, executive lounge access, and premium bath amenities. The Executive Suite offers a spacious environment for work and relaxation, with stunning views of the ocean.',
            amenities: ['65 m²', 'King Bed', 'Ocean View', 'Lounge Access', 'Bathtub', 'Work Desk', 'Separate Living Room', 'Premium Toiletries'],
            images: [
                'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1591088398332-8a7791972843?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'family': {
            title: 'Family Studio',
            price: '$350',
            description: 'Spacious accommodation designed for families, featuring two queen beds and a kitchenette. This studio provides a home-away-from-home experience with plenty of space for everyone to relax.',
            amenities: ['55 m²', '2 Queen Beds', 'Garden View', 'Kitchenette', 'Gaming Console', 'Kids Area', 'Dining Table', 'Microwave'],
            images: [
                'https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1616486338812-3a47728331a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'villa': {
            title: 'Ocean View Villa',
            price: '$800',
            description: 'A private sanctuary with direct beach access, private pool, and stunning sunset views. The Ocean View Villa is the epitome of luxury island living, offering complete privacy and exclusive services.',
            amenities: ['120 m²', 'King Bed', 'Ocean Front', 'Private Pool', 'Outdoor Shower', 'Hammock', 'Private Garden', 'Butler Service'],
            images: [
                'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1473186578169-21484728384d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        },
        'penthouse': {
            title: 'Presidential Penthouse',
            price: '$1,200',
            description: 'Unmatched luxury on the top floor. Features a private terrace, jacuzzi, dining area, and 24-hour butler service. The Presidential Penthouse is our jewel, hosting dignitaries and celebrities with discreet and impeccable service.',
            amenities: ['150 m²', '2 Bedrooms', 'Panoramic View', 'Private Terrace', 'Jacuzzi', 'Butler Service', 'Grand Piano', 'Private Chef Option'],
            images: [
                'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
                'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80'
            ]
        }
    };

    const roomSlider = document.getElementById('room-slider');

    if (roomSlider) {
        // Get Room ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        const roomId = urlParams.get('id');
        const room = roomData[roomId];

        if (room) {
            // Populate Data
            document.title = `${room.title} | Hotel Aphrodite`;
            document.getElementById('room-title').textContent = room.title;
            document.getElementById('room-price').innerHTML = `${room.price} <span style="font-size: 1rem; color: #666; font-weight: 400;">/ night</span>`;
            document.getElementById('room-description').textContent = room.description;

            const amenitiesList = document.getElementById('room-amenities');
            room.amenities.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `&#10003; ${item}`;
                amenitiesList.appendChild(li);
            });

            // Populate Slider
            const sliderDots = document.getElementById('slider-dots');

            room.images.forEach((imgSrc, index) => {
                // Slide
                const slide = document.createElement('div');
                slide.className = 'slide';
                slide.innerHTML = `<img src="${imgSrc}" alt="${room.title} Image ${index + 1}">`;
                roomSlider.appendChild(slide);

                // Dot
                const dot = document.createElement('div');
                dot.className = index === 0 ? 'dot active' : 'dot';
                dot.addEventListener('click', () => goToSlide(index));
                sliderDots.appendChild(dot);
            });

            // Slider Logic
            let currentSlide = 0;
            const totalSlides = room.images.length;
            const prevBtn = document.getElementById('prev-btn');
            const nextBtn = document.getElementById('next-btn');

            function updateSlider() {
                roomSlider.style.transform = `translateX(-${currentSlide * 100}%)`;
                document.querySelectorAll('.dot').forEach((dot, index) => {
                    dot.classList.toggle('active', index === currentSlide);
                });
            }

            function goToSlide(index) {
                currentSlide = index;
                updateSlider();
            }

            function nextSlide() {
                currentSlide = (currentSlide + 1) % totalSlides;
                updateSlider();
            }

            function prevSlide() {
                currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
                updateSlider();
            }

            nextBtn.addEventListener('click', nextSlide);
            prevBtn.addEventListener('click', prevSlide);

            // Auto Play
            setInterval(nextSlide, 5000);

        } else {
            // Handle invalid room ID
            document.querySelector('.room-details-section').innerHTML = '<div class="container"><h2>Room not found</h2><p>Please return to the <a href="rooms.html">Rooms page</a>.</p></div>';
        }
    }
});
