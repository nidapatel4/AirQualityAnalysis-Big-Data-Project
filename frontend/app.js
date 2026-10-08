const navButtons = document.querySelectorAll('.nav-btn');
const panels = document.querySelectorAll('.panel');

navButtons.forEach((button) => {
  button.addEventListener('click', () => {
    navButtons.forEach((btn) => btn.classList.remove('active'));
    panels.forEach((panel) => panel.classList.remove('active-panel'));
    button.classList.add('active');
    const target = document.getElementById(button.dataset.target);
    if (target) {
      target.classList.add('active-panel');
    }
    requestAnimationFrame(() => {
      Object.values(chartRegistry).forEach((chart) => chart.resize());
    });
  });
});

const chartRegistry = {};
let aqiRows = [];
let stationAverages = [];

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function renderKpis(data) {
  const kpis = [
    ['Total Observations', data.total_observations || 0],
    ['Stations', data.number_of_stations || 0],
    ['Avg PM2.5', `${data.average_pm25 || 0} µg/m³`],
    ['Max PM2.5', `${data.maximum_pm25 || 0} µg/m³`],
    ['Min PM2.5', `${data.minimum_pm25 || 0} µg/m³`],
    ['Most Common AQI', data.most_common_aqi_category || 'N/A'],
    ['Most Polluted Station', data.most_polluted_station?.station_id || 'N/A'],
    ['Days Analyzed', data.days_analyzed || 0],
  ];

  const container = document.getElementById('kpi-grid');
  container.innerHTML = kpis
    .map(
      ([label, value]) => `
        <div class="kpi-card">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </div>
      `
    )
    .join('');
}

function buildBarChart(canvasId, labels, values, color = '#2f6fed') {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (chartRegistry[canvasId]) {
    chartRegistry[canvasId].destroy();
  }
  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Count',
        data: values,
        backgroundColor: color,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
        animation: false,
        scales: {
          y: { beginAtZero: true },
        },
    },
  });
  return chartRegistry[canvasId];
}

function buildLineChart(canvasId, labels, values, label = 'Value', color = '#2f6fed') {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (chartRegistry[canvasId]) {
    chartRegistry[canvasId].destroy();
  }
  chartRegistry[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        borderColor: color,
        backgroundColor: 'rgba(47,111,237,0.1)',
        fill: true,
        tension: 0.2,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: false },
      },
    },
  });
  return chartRegistry[canvasId];
}

async function loadOverview() {
  const overview = await fetchJson('/api/overview');
  renderKpis(overview);

  const aqiDistribution = overview.aqi_category_distribution || [];
  buildBarChart(
    'aqiBarChart',
    aqiDistribution.map(item => item.category),
    aqiDistribution.map(item => item.count),
    '#2f6fed'
  );

  const topStations = await fetchJson('/api/pm25/top-stations');
  buildBarChart(
    'pm25BarChart',
    topStations.slice(0, 8).map(item => item.station_id),
    topStations.slice(0, 8).map(item => Number(item.average_pm25)),
    '#ef4444'
  );

  aqiRows = await fetchJson('/api/aqi');
  const trend = aggregateAqiByDate(aqiRows, '', 60);
  buildLineChart(
    'aqiTrendChart',
    trend.map(item => item.date),
    trend.map(item => item.count),
    'Total AQI observations',
    '#2f6fed'
  );
}

async function loadAqiAnalysis() {
  const [aqiData, stations] = await Promise.all([
    fetchJson('/api/aqi'),
    fetchJson('/api/pm25/top-stations'),
  ]);
  aqiRows = aqiData;
  stationAverages = stations;

  const categoryOptions = document.getElementById('aqiCategoryFilter');
  const categories = [...new Set(aqiData.map((item) => item.aqi_bucket))].sort();
  const selectedCategory = categoryOptions.value;
  categoryOptions.innerHTML = '<option value="">All AQI categories</option>' +
    categories.map((category) => `<option value="${category}">${category}</option>`).join('');
  categoryOptions.value = selectedCategory;
  categoryOptions.onchange = renderAnalysisCharts;
  renderAnalysisCharts();
  renderPm25Charts();
}

function aggregateAqiByDate(rows, selectedCategory, limit) {
  const totals = new Map();
  rows.forEach((row) => {
    if (selectedCategory && row.aqi_bucket !== selectedCategory) {
      return;
    }
    totals.set(row.date, (totals.get(row.date) || 0) + Number(row.count));
  });
  return [...totals.entries()]
    .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
    .slice(-limit)
    .map(([date, count]) => ({ date, count }));
}

function renderAnalysisCharts() {
  const selectedCategory = document.getElementById('aqiCategoryFilter').value;
  const rows = selectedCategory
    ? aqiRows.filter((row) => row.aqi_bucket === selectedCategory)
    : aqiRows;
  const totals = rows.reduce((counts, row) => {
    counts[row.aqi_bucket] = (counts[row.aqi_bucket] || 0) + Number(row.count);
    return counts;
  }, {});
  const categories = selectedCategory ? [selectedCategory] : Object.keys(totals).sort();
  buildBarChart(
    'aqiAnalysisChart',
    categories,
    categories.map((category) => totals[category] || 0),
    '#17a2b8'
  );

  const trend = aggregateAqiByDate(aqiRows, selectedCategory, 60);
  buildLineChart(
    'aqiTrendDetailChart',
    trend.map((item) => item.date),
    trend.map((item) => item.count),
    selectedCategory || 'All AQI categories',
    '#2f6fed'
  );
}

function renderPm25Charts() {
  const top = stationAverages.slice(0, 10);
  buildBarChart(
    'topStationsChart',
    top.map((item) => item.station_id),
    top.map((item) => Number(item.average_pm25)),
    '#ef4444'
  );
}

async function loadGeography() {
  const summary = await fetchJson('/api/geography');
  const chartData = summary.station_count_by_state || [];
  buildBarChart(
    'stateCoverageChart',
    chartData.map(item => item.state),
    chartData.map(item => item.count),
    '#22c55e'
  );
}

async function loadLiveMonitoring() {
  const data = await fetchJson('/api/live-monitoring');
  const cards = [
    ['Highest Station Average', data.highest_station?.average_pm25 == null
      ? 'N/A'
      : `${Number(data.highest_station.average_pm25).toFixed(2)} µg/m³`],
    ['Station', data.highest_station?.station_id || 'N/A'],
    ['Stations Analyzed', data.stations_analyzed || 0],
    ['Station Averages > 100 µg/m³', data.stations_above_threshold || 0],
  ];
  const container = document.getElementById('liveMonitoringCards');
  container.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="kpi-card">
          <div class="label">${label}</div>
          <div class="value">${value}</div>
        </div>
      `
    )
    .join('');
  document.getElementById('monitoringStationsBody').innerHTML =
    (data.top_stations || []).map((item) => `
      <tr>
        <td>${item.station_id}</td>
        <td>${Number(item.average_pm25).toFixed(2)} µg/m³</td>
      </tr>
    `).join('');
}

async function loadDatasetInfo() {
  const info = await fetchJson('/api/dataset-info');
  const container = document.getElementById('datasetInfo');
  const rows = [
    ['Dataset name', info.name],
    ['Time period', info.time_period],
    ['Number of records', info.records],
    ['Number of columns', info.columns.length],
    ['Stations', info.stations],
    ['HDFS location', info.hdfs_location],
    ['MapReduce jobs', info.mapreduce_jobs.join(', ')],
    ['Missing values', info.missing_values],
  ];
  container.innerHTML = `
    <table>
      <tbody>
        ${rows.map(([label, value]) => `<tr><th>${label}</th><td>${value}</td></tr>`).join('')}
      </tbody>
    </table>
  `;
}

async function initDashboard() {
  await Promise.all([
    loadOverview(),
    loadAqiAnalysis(),
    loadGeography(),
    loadLiveMonitoring(),
    loadDatasetInfo(),
  ]);
}

initDashboard().catch((error) => {
  console.error('Dashboard could not load:', error);
});
