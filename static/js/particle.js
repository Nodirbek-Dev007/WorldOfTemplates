function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = [];
  const particleCount = 100;

  class Particle {
      constructor() {
          this.x = Math.random() * canvas.width;
          this.y = Math.random() * canvas.height;
          this.size = Math.random() * 2 + 1;
          this.speedX = Math.random() * 0.5 - 0.25;
          this.speedY = Math.random() * 0.5 - 0.25;
      }

      update() {
          this.x += this.speedX;
          this.y += this.speedY;
          if (this.size > 0.2) this.size -= 0.01;
      }

      draw() {
          ctx.fillStyle = 'rgba(0, 255, 136, 0.8)';
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
          ctx.fill();
      }
  }

  for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
  }

  function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach((particle, index) => {
          particle.update();
          particle.draw();
          if (particle.size <= 0.2) {
              particles.splice(index, 1);
              particles.push(new Particle());
          }
      });
      requestAnimationFrame(animate);
  }

  animate();
}

// GSAP Scroll Animations
document.addEventListener('DOMContentLoaded', () => {
  gsap.from('.banner_taital', { opacity: 0, y: 50, duration: 1.5, ease: 'power3.out' });
  gsap.from('.search-form', { opacity: 0, y: 30, duration: 1.5, delay: 0.5, ease: 'power3.out' });

  gsap.utils.toArray('.related-presentations').forEach(card => {
      gsap.from(card, {
          opacity: 0,
          y: 50,
          duration: 1,
          scrollTrigger: {
              trigger: card,
              start: 'top 80%',
              toggleActions: 'play none none none'
          }
      });
  });

  initParticles();
});