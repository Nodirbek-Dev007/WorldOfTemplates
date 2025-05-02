// Parallax Effect
window.addEventListener('scroll', () => {
  const parallax = document.querySelector('.parallax-bg');
  const scrollPosition = window.pageYOffset;
  parallax.style.transform = `translateY(${scrollPosition * 0.5}px)`;
});