// City mapping
const cityData = {
    us: ["New York", "San Francisco", "Austin", "Chicago", "Seattle"],
    gb: ["London", "Manchester", "Birmingham", "Edinburgh"],
    ca: ["Toronto", "Vancouver", "Montreal", "Ottawa"],
    au: ["Sydney", "Melbourne", "Brisbane", "Perth"],
    in: ["Bengaluru", "Hyderabad", "Mumbai", "Pune", "Delhi"],
    de: ["Berlin", "Munich", "Frankfurt", "Hamburg"],
    fr: ["Paris", "Lyon", "Marseille", "Toulouse"],
    it: ["Rome", "Milan", "Naples", "Turin"],
    es: ["Madrid", "Barcelona", "Valencia", "Seville"],
    nl: ["Amsterdam", "Rotterdam", "The Hague", "Utrecht"],
    ch: ["Zurich", "Geneva", "Basel", "Lausanne"],
    at: ["Vienna", "Salzburg", "Graz", "Linz"],
    be: ["Brussels", "Antwerp", "Ghent", "Bruges"],
    pl: ["Warsaw", "Kraków", "Wrocław", "Gdańsk"],
    br: ["São Paulo", "Rio de Janeiro", "Brasília", "Curitiba"],
    mx: ["Mexico City", "Guadalajara", "Monterrey", "Tijuana"],
    za: ["Johannesburg", "Cape Town", "Durban", "Pretoria"],
    nz: ["Auckland", "Wellington", "Christchurch", "Hamilton"],
    sg: ["Singapore"]
};

// Global charts
let barChartInstance = null;
let doughnutChartInstance = null;

// Update cities
function updateCities() {
    const country = document.getElementById("countrySelect").value;
    const citySelect = document.getElementById("citySelect");

    citySelect.innerHTML = '<option value="">All Cities</option>';

    if (country && cityData[country]) {
        citySelect.disabled = false;
        cityData[country].forEach(city => {
            const option = document.createElement("option");
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    } else {
        citySelect.disabled = true;
    }
}

// Fetch new data
async function triggerJobSearch() {
    const country = document.getElementById("countrySelect").value;
    const city = document.getElementById("citySelect").value;
    const target = document.getElementById("targetSelect").value;
    const statusMsg = document.getElementById("statusMsg");
    const searchBtn = document.getElementById("searchBtn");

    if (!country) {
        alert("Please select a country.");
        return;
    }

    // UI loading state
    statusMsg.classList.remove("hidden");
    searchBtn.disabled = true;
    searchBtn.classList.add("opacity-50");

    const payload = { country, city, target };

    await fetch("/api/sync-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    // Reset UI
    statusMsg.classList.add("hidden");
    searchBtn.disabled = false;
    searchBtn.classList.remove("opacity-50");

    loadDashboardCharts();
}

// Load Insights
async function loadInsights() {
    const response = await fetch("/api/insights");
    const data = await response.json();

    const insightsList = document.getElementById("insightsList");
    insightsList.innerHTML = "";

    data.insights.forEach(text => {
        const li = document.createElement("li");
        li.innerHTML = text;
        insightsList.appendChild(li);
    });
}

// Render charts
async function loadDashboardCharts() {
    // Load textual insights
    loadInsights();

    const response = await fetch("/api/top-skills");
    const data = await response.json();

    const labels = data.map(item => item.name.toUpperCase());
    const counts = data.map(item => item.count);

    // Aggregate categories
    const catCounts = {};
    data.forEach(item => {
        catCounts[item.category] = (catCounts[item.category] || 0) + item.count;
    });

    // Reset charts
    if (barChartInstance) barChartInstance.destroy();
    if (doughnutChartInstance) doughnutChartInstance.destroy();

    // Bar Chart
    const barCtx = document.getElementById('barChart').getContext('2d');
    const gradient = barCtx.createLinearGradient(0, 0, 500, 0);
    gradient.addColorStop(0, '#3b82f6');
    gradient.addColorStop(1, '#8b5cf6');

    barChartInstance = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Job Postings',
                data: counts,
                backgroundColor: gradient,
                borderRadius: 4,
                barThickness: 16
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            // THIS FIXES THE HOVER ALIGNMENT FOR HORIZONTAL BARS
            interaction: {
                mode: 'index',
                axis: 'y',
                intersect: false,
            },
            layout: {
                padding: { left: 10, right: 25, top: 10, bottom: 10 }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    padding: 10
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { precision: 0 }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        autoSkip: false,
                        font: { size: 12, weight: '500' },
                        padding: 8
                    }
                }
            },
            animation: { duration: 1200, easing: 'easeOutQuart' }
        }
    });

    // Doughnut Chart
    const dogCtx = document.getElementById('doughnutChart').getContext('2d');
    const doughnutColors = [
        'rgba(59, 130, 246, 0.85)',
        'rgba(16, 185, 129, 0.85)',
        'rgba(245, 158, 11, 0.85)',
        'rgba(239, 68, 68, 0.85)',
        'rgba(139, 92, 246, 0.85)',
        'rgba(236, 72, 153, 0.85)',
        'rgba(14, 165, 233, 0.85)',
        'rgba(249, 115, 22, 0.85)'
    ];

    doughnutChartInstance = new Chart(dogCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(catCounts),
            datasets: [{
                data: Object.values(catCounts),
                backgroundColor: doughnutColors,
                borderWidth: 2,
                borderColor: '#ffffff',
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 16, font: { size: 12 } }
                }
            }
        }
    });
}

// Init
window.onload = loadDashboardCharts;
