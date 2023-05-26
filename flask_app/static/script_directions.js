let map;

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    map = new Map(document.getElementById("map"), {
    center: { lat: 47.85962056662854, lng: -121.96521421349361 },
    zoom: 16,
    });

    const marker = new google.maps.Marker({
        position: { lat: 47.85962056662854, lng: -121.96521421349361 },
        map : map,
        animation: google.maps.Animation.BOUNCE
    });

    const infoWindow = new google.maps.InfoWindow({
        content: '<p>Next to the Pizza Hut and Starbucks!</p>'
    });

    infoWindow.open(map, marker)
}

initMap();