---
title: "Guldesteyek Ji Stranên Biyanî"
date: 2026-05-13T02:56:00+03:00
tags: ['personal', 'kurdî', 'stranbêj', 'stran']
draft: false
layout: stran
url: /stranen_biyani/
---

2 sal berê min wilo gotibû
> Pişti min guldesteyek ser stranên kurdewarî weşand, gelek kes (0) ji min pirsî "ma tu stranên biyani guhdar nakî?".  
Xwedê efû bike, bersiva min "belê, guhdar dikim" bû.   
> Berî her tiştî gerek hûn zanibin ku ez nikarim hemû stranan li vir parve bikim.   
Gelek neşîd û stranên min jê hez dikir hebûn; hin ji wan winda bûn, hin yesax kirin, hin jî ez nevêrim parve bikim.

û bi tenê strana _Yaşamadın Sen_ parve kiribû. Bi rastî wê demê ji min nedihat ku lînkên van stranan bigerim û parve bikim. \
Êdî bes e. 

## Alpay
### Fabrika Kızı
{{< youtube-lazy 9-garWPAdHk >}}

### Yanımda Kal
{{< youtube-lazy  3jML-DXiihg >}}

## Ahmet Kaya
### Yaşamadın Sen
{{< youtube-lazy VrGxsbBCO-Q >}}

<!-- 
### Öyle Bir Yerdeyim ki
{{< youtube-lazy EeaD3vZmxKI >}}
 -->

### Gayri Gider Oldum
{{< youtube-lazy K1W6eFt5B0Q >}}

### Başkaldırıyorum
{{< youtube-lazy jxp6pHXBRmE >}}

### Geçmiyor Günler
{{< youtube-lazy EWl7Y6eIkAk >}}

### Yollarına Baka Baka
{{< youtube-lazy M9DuW84IVBE >}}

## Johnny Paycheck
### Someone to give my love to
{{< youtube-lazy KXV3yR80d5w>}}
### [It Won’t Be Long] And I’ll Be Hating You

{{< youtube-lazy oQq84dPKjd8 >}}

## Mustafa Keser
### Aklımda Fikrimde Hep Sen Varsın (Tutku)
<!-- {{< youtube-lazy 4cbRQ6AM6rw >}} -->
{{< youtube-lazy LyCGEM7ewsk >}}

## Elvis Presley
### Can't Help Falling in Love
{{< youtube-lazy vlu9lJAj1Mk >}}

## Ferdi Tayfur
### Merak Etme Sen
{{< youtube-lazy -zYPp_MJ9Wg >}}

## Barış Manço
### Ahmet Beyin Ceketi
{{< youtube-lazy cs0zzuzA4_A >}}
 

## Alan Walker
### Lost Control
{{< youtube-lazy vi6v0MOWp2Q >}}

### On My Way
{{< youtube-lazy Hkvopu9hVd8 >}}


### Faded
{{< youtube-lazy pIWaVJPl0-c >}}

## NOJH CHOIRS & DRAMA (?)
### The Ballad of Sweeney Todd
{{< youtube-lazy 1ujRsV9Q_kk >}}

## Edip Akbayram
### Aldırma Gönül
{{< youtube-lazy 8yk0dNCsN2Y >}}
 
## Full Metal Alchemist
{{< youtube-lazy Sz470nhuyMY >}}

## Ebu Ali
### Hebbet Kerrih
{{< youtube-lazy 8kDf4KjDBE0 >}}

<!-- 
{{< youtube-lazy  >}}
 -->
 



<script>
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

</script>
