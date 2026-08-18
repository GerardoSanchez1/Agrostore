document.addEventListener('DOMContentLoaded', () => {
    // Mobile hamburger menu
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Product image carousel/gallery
    const mainImage = document.getElementById('gallery-main-img');
    const thumbnails = document.querySelectorAll('.gallery-thumb');

    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const newSrc = this.getAttribute('data-src');
                if (newSrc) {
                    mainImage.src = newSrc;
                }
                // Update active state on thumbnails
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Wishlist toggle (AJAX POST with CSRF)
    const wishlistButtons = document.querySelectorAll('.wishlist-toggle');
    
    wishlistButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const itemId = this.dataset.itemId;
            const url = `/lista-deseos/toggle/${itemId}/`;
            
            // Get CSRF token from a meta tag or cookie
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken') || window.CSRF_TOKEN;
            
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.added === true) {
                        this.classList.add('in-wishlist', 'wishlisted', 'btn-wishlisted');
                        this.classList.remove('btn-wishlist');
                        
                        const span = this.querySelector('span');
                        if (span) {
                            this.innerHTML = '<i class="fas fa-heart"></i> <span>En tu Lista de Deseos</span>';
                        } else {
                            this.innerHTML = '<i class="fas fa-heart"></i>';
                        }
                    } else if (data.added === false) {
                        this.classList.remove('in-wishlist', 'wishlisted', 'btn-wishlisted');
                        this.classList.add('btn-wishlist');
                        
                        const span = this.querySelector('span');
                        if (span) {
                            this.innerHTML = '<i class="far fa-heart"></i> <span>Agregar a Lista de Deseos</span>';
                        } else {
                            this.innerHTML = '<i class="far fa-heart"></i>';
                        }
                    }
                } else if (response.status === 403) {
                    // Redirect to login if not authenticated
                    window.location.href = '/iniciar-sesion/?next=' + window.location.pathname;
                }
            } catch (error) {
                console.error('Error toggling wishlist:', error);
            }
        });
    });

    // Product description/details tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    if (tabBtns.length > 0 && tabPanels.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanels.forEach(p => p.classList.remove('active'));
                
                btn.classList.add('active');
                const targetId = 'tab-' + btn.getAttribute('data-tab');
                const targetPanel = document.getElementById(targetId);
                if (targetPanel) {
                    targetPanel.classList.add('active');
                }
            });
        });
    }

    // Helper function to get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
