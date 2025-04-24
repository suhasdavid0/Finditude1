document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("preferencesForm");
    const resultsList = document.getElementById("results-list");
    const favoritesList = document.getElementById("favorites-list");
    const resultsSection = document.getElementById("results");
    const toggleThemeBtn = document.getElementById("toggle-theme");
    const sortOptions = document.getElementById("sortOptions");

    let spotsData = [
        { name: "Central Park", type: "Park", tags: ["Relax", "Hangout"], popularity: 5, price: "Free", lat: 40.785091, lng: -73.968285 },
        { name: "Beachfront Cafe", type: "Restaurant", tags: ["Relax", "Hangout"], popularity: 4, price: "$$", lat: 34.0195, lng: -118.4912 },
        { name: "Music of Modern Art", type: "Muisc", tags: ["Music"], popularity: 5, price: "$$", lat: 40.761436, lng: -73.977621 }
        


    ];

    let favoriteSpots = JSON.parse(localStorage.getItem("favorites")) || [];

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const preferences = [];
        formData.forEach((_, key) => preferences.push(key));

        let filteredSpots = spotsData.filter(spot => preferences.some(pref => spot.tags.includes(pref)));

        displayResults(filteredSpots);
        resultsSection.style.display = "block";
    });

    function displayResults(spots) {
        resultsList.innerHTML = "";
        spots.forEach(spot => {
            const listItem = document.createElement("li");
            listItem.textContent = `${spot.name} - ${spot.type} (Popularity: ${spot.popularity}, Price: ${spot.price})`;

            const favoriteBtn = document.createElement("button");
            favoriteBtn.textContent = favoriteSpots.includes(spot.name) ? "Unfavorite" : "Favorite";
            favoriteBtn.addEventListener("click", () => toggleFavorite(spot.name));

            listItem.appendChild(favoriteBtn);
            resultsList.appendChild(listItem);
        });
        displayFavorites();
        updateMap(spots);
    }

    function toggleFavorite(spotName) {
        if (favoriteSpots.includes(spotName)) {
            favoriteSpots = favoriteSpots.filter(fav => fav !== spotName);
        } else {
            favoriteSpots.push(spotName);
        }
        localStorage.setItem("favorites", JSON.stringify(favoriteSpots));
        displayFavorites();
    }

    function displayFavorites() {
        favoritesList.innerHTML = "";
        favoriteSpots.forEach(spotName => {
            const listItem = document.createElement("li");
            listItem.textContent = spotName;
            favoritesList.appendChild(listItem);
        });
    }

    sortOptions.addEventListener("change", function () {
        let sortedSpots = [...spotsData];
        if (this.value === "popularity") {
            sortedSpots.sort((a, b) => b.popularity - a.popularity);
        } else if (this.value === "price") {
            sortedSpots.sort((a, b) => a.price.length - b.price.length);
        }
        displayResults(sortedSpots);
    });

    function updateMap(spots) {
        const map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 40.7128, lng: -74.006 },
            zoom: 12,
        });

        spots.forEach(spot => {
            new google.maps.Marker({
                position: { lat: spot.lat, lng: spot.lng },
                map,
                title: spot.name,
            });
        });
    }

    toggleThemeBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        localStorage.setItem("darkMode", document.body.classList.contains("dark-mode"));
    });

    if (localStorage.getItem("darkMode") === "true") {
        document.body.classList.add("dark-mode");
    }

    displayFavorites();

    // Load Google Maps API
    const script = document.createElement("script");
    script.src = "https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap";
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});
