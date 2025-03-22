document.addEventListener('DOMContentLoaded', function() {
  const lazyVideos = document.querySelectorAll('.youtube-lazy');
  
  function createYouTubeEmbed(container) {
    const videoId = container.getAttribute('data-id');
    const iframe = document.createElement('iframe');
    
    iframe.setAttribute('src', 'https://www.youtube.com/embed/' + videoId + '?autoplay=1');
    iframe.setAttribute('frameborder', '0');
    iframe.setAttribute('allowfullscreen', '1');
    iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
    
    container.innerHTML = '';
    container.appendChild(iframe);
    container.classList.add('active');
  }
  
  // Add click event to the container
  lazyVideos.forEach(function(video) {
    video.addEventListener('click', function(e) {
      e.preventDefault();
      createYouTubeEmbed(this);
    });
  });
  
  // Add click events to thumbnails and play buttons specifically
  document.querySelectorAll('.youtube-lazy .thumbnail, .youtube-lazy .play-button').forEach(function(element) {
    element.addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent double triggering
      createYouTubeEmbed(this.closest('.youtube-lazy'));
    });
  });
  
  // Check if thumbnails failed to load and replace with a placeholder
  document.querySelectorAll('.youtube-lazy .thumbnail').forEach(function(img) {
    img.addEventListener('error', function() {
      this.src = 'data:image/svg+xml;charset=UTF-8,%3Csvg%20width%3D%22800%22%20height%3D%22450%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20800%20450%22%20preserveAspectRatio%3D%22none%22%3E%3Cdefs%3E%3Cstyle%20type%3D%22text%2Fcss%22%3E%23holder_1887ea5a3a7%20text%20%7B%20fill%3A%23999%3Bfont-weight%3Anormal%3Bfont-family%3AArial%2C%20Helvetica%2C%20Open%20Sans%2C%20sans-serif%2C%20monospace%3Bfont-size%3A40pt%20%7D%20%3C%2Fstyle%3E%3C%2Fdefs%3E%3Cg%20id%3D%22holder_1887ea5a3a7%22%3E%3Crect%20width%3D%22800%22%20height%3D%22450%22%20fill%3D%22%23373940%22%3E%3C%2Frect%3E%3Cg%3E%3Ctext%20x%3D%22289.71875%22%20y%3D%22243.9%22%3EYouTube%20Video%3C%2Ftext%3E%3C%2Fg%3E%3C%2Fg%3E%3C%2Fsvg%3E';
      this.style.objectFit = 'contain';
    });
  });
});
