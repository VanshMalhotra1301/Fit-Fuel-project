document.addEventListener('DOMContentLoaded', function() {
    
    // ---------------------------------------------------------
    // 1. TYPING ANIMATION
    // ---------------------------------------------------------
    // Ensure you have <span id="typing-element"></span> in your HTML content
    if(document.getElementById('typing-element')) {
        new Typed('#typing-element', {
            strings: [
                'Optimize Your Macros.',
                'Build Muscle Faster.',
                'Lose Fat Smarter.',
                'Fuel Your Performance.'
            ],
            typeSpeed: 40,
            backSpeed: 20,
            loop: true,
            showCursor: true,
            cursorChar: '▋'
        });
    }

    // ---------------------------------------------------------
    // 2. SCROLL REVEAL
    // ---------------------------------------------------------
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show-content');
            }
        });
    });

    // Targeting common elements. Ensure your CSS handles .hidden-content
    const hiddenElements = document.querySelectorAll('.card, .form-container, h1, h2, .hero-text');
    hiddenElements.forEach((el) => {
        el.classList.add('hidden-content');
        observer.observe(el);
    });

    // ---------------------------------------------------------
    // 3. 3D CARD TILT EFFECT
    // ---------------------------------------------------------
    const cards = document.querySelectorAll('.meal-card-3d, .card'); 

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const xRotation = -((y - rect.height / 2) / 20);
            const yRotation = ((x - rect.width / 2) / 20);
            
            card.style.transform = `perspective(1000px) rotateX(${xRotation}deg) rotateY(${yRotation}deg) scale(1.02)`;
            card.style.border = '1px solid rgba(199, 112, 240, 0.5)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
            card.style.border = '1px solid rgba(255, 255, 255, 0.1)';
        });
    });

    // ---------------------------------------------------------
    // 4. "HEARTBEAT" CONSTELLATION BACKGROUND
    // ---------------------------------------------------------
    const canvas = document.getElementById('constellation-bg');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        let particlesArray;
        
        const colorPrimary = 'rgba(199, 112, 240, 1)'; 
        
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        class Particle {
            constructor(x, y, directionX, directionY, size, color) {
                this.x = x; this.y = y;
                this.directionX = directionX; this.directionY = directionY;
                this.size = size;
                this.baseSize = size;
                this.color = color;
                this.angle = Math.random() * 6.2;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
            update() {
                if (this.x > canvas.width || this.x < 0) this.directionX = -this.directionX;
                if (this.y > canvas.height || this.y < 0) this.directionY = -this.directionY;
                this.x += this.directionX;
                this.y += this.directionY;

                this.angle += 0.05; 
                this.size = this.baseSize + Math.sin(this.angle) * 1.5;
                if(this.size < 0) this.size = 0.1;

                this.draw();
            }
        }

        function init() {
            particlesArray = [];
            let numberOfParticles = (canvas.height * canvas.width) / 9000; // Adjusted density
            for (let i = 0; i < numberOfParticles; i++) {
                let size = (Math.random() * 2) + 1;
                let x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
                let y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
                let directionX = (Math.random() * 1) - 0.5;
                let directionY = (Math.random() * 1) - 0.5;
                
                particlesArray.push(new Particle(x, y, directionX, directionY, size, colorPrimary));
            }
        }

        function connect() {
            for (let a = 0; a < particlesArray.length; a++) {
                for (let b = a; b < particlesArray.length; b++) {
                    let distance = ((particlesArray[a].x - particlesArray[b].x) ** 2) + 
                                   ((particlesArray[a].y - particlesArray[b].y) ** 2);
                    
                    if (distance < (canvas.width / 7) * (canvas.height / 7)) {
                        let opacityValue = 1 - (distance / 20000);
                        ctx.strokeStyle = `rgba(199, 112, 240, ${opacityValue})`;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
                        ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
                        ctx.stroke();
                    }
                }
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            ctx.clearRect(0, 0, innerWidth, innerHeight);
            
            for (let i = 0; i < particlesArray.length; i++) {
                particlesArray[i].update();
            }
            connect();
        }

        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            init();
        });

        init();
        animate();
    }
    
    // ---------------------------------------------------------
    // 5. BUTTON LOADING STATE
    // ---------------------------------------------------------
    const form = document.getElementById('fitForm');
    if (form) {
        form.addEventListener('submit', function(e){
            const btn = form.querySelector('button[type="submit"]');
            btn.innerHTML = '<span class="loader"></span> CRUNCHING DATA...';
            btn.style.opacity = '0.9';
            btn.style.transform = 'scale(0.95)';
        });
    }
});
