import * as THREE from 'https://unpkg.com/three@0.153.0/build/three.module.js';
import { OrbitControls } from 'https://unpkg.com/three@0.153.0/examples/jsm/controls/OrbitControls.js';

// VRP Solution Visualization using Three.js
// Loads vrp_solution.json and draws routes, stops, and animates vehicles

// --- Load VRP solution from JSON ---
async function loadVRPSolution() {
  const response = await fetch('vrp_solution.json');
  if (!response.ok) {
    alert('Could not load vrp_solution.json. Please run the Python script and ensure the file exists.');
    throw new Error('vrp_solution.json not found');
  }
  const data = await response.json();
  return data.routes;
}

// --- Visualize the routes and stops ---
function visualizeRoutes(routes, scene) {
  const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffff00, 0x888888]; // Different color per vehicle
  routes.forEach((route, i) => {
    // Draw route as a colored line
    const material = new THREE.LineBasicMaterial({ color: colors[i % colors.length], linewidth: 3 });
    const points = route.map(pt => new THREE.Vector3(pt.location[0], pt.location[1], 0));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const line = new THREE.Line(geometry, material);
    scene.add(line);
    // Draw stops as blue spheres
    route.forEach((pt, idx) => {
      const sphereGeometry = new THREE.SphereGeometry(0.6, 16, 16);
      const sphereMaterial = new THREE.MeshBasicMaterial({ color: 0x3333ff });
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      sphere.position.set(pt.location[0], pt.location[1], 0);
      scene.add(sphere);
      // Optionally add node index as a label (simple text sprite)
      addTextLabel(scene, `${pt.node}`, pt.location[0], pt.location[1]);
    });
  });
}

// --- Add a simple text label at (x, y) ---
function addTextLabel(scene, text, x, y) {
  const canvas = document.createElement('canvas');
  const size = 64;
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  ctx.font = 'bold 28px Arial';
  ctx.fillStyle = '#222';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, size/2, size/2);
  const texture = new THREE.CanvasTexture(canvas);
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.scale.set(2, 2, 1);
  sprite.position.set(x, y, 1.2);
  scene.add(sprite);
}

// --- Animate vehicles along their routes ---
function createVehicleMarkers(routes, scene) {
  const vehicleMarkers = [];
  const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xff00ff, 0x00ffff, 0xffff00, 0x888888];
  routes.forEach((route, i) => {
    const vehicleGeometry = new THREE.SphereGeometry(1, 24, 24);
    const vehicleMaterial = new THREE.MeshBasicMaterial({ color: colors[i % colors.length] });
    const marker = new THREE.Mesh(vehicleGeometry, vehicleMaterial);
    // Place at first stop
    marker.position.set(route[0].location[0], route[0].location[1], 1.5);
    scene.add(marker);
    vehicleMarkers.push({ marker, route, routeIndex: 0, t: 0 });
  });
  return vehicleMarkers;
}

// --- Main Scene Setup ---
async function main() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  // Load VRP solution first to compute bounds
  let routes = [];
  try {
    routes = await loadVRPSolution();
  } catch (e) {
    // Error already alerted
  }

  // --- Compute bounding box of all points ---
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  routes.forEach(route => {
    route.forEach(pt => {
      minX = Math.min(minX, pt.location[0]);
      maxX = Math.max(maxX, pt.location[0]);
      minY = Math.min(minY, pt.location[1]);
      maxY = Math.max(maxY, pt.location[1]);
    });
  });
  // Add some padding
  const pad = 8;
  minX -= pad; maxX += pad; minY -= pad; maxY += pad;
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const spanX = maxX - minX;
  const spanY = maxY - minY;
  const maxSpan = Math.max(spanX, spanY);

  // --- Camera setup to fit the graph ---
  const fov = 60; // degrees
  const aspect = window.innerWidth / window.innerHeight;
  // Calculate distance so the graph fits vertically
  const fitHeight = maxSpan;
  let fitDist = fitHeight / (2 * Math.tan((fov * Math.PI) / 360));
  const camera = new THREE.PerspectiveCamera(fov, aspect, 0.1, 2000);
  camera.position.set(centerX, centerY, fitDist * 1.25);
  camera.lookAt(centerX, centerY, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // --- OrbitControls for zoom and rotate ---
  // Use global OrbitControls if loaded via <script>
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(centerX, centerY, 0);
  controls.enableDamping = true;
  controls.dampingFactor = 0.12;
  controls.screenSpacePanning = false;
  controls.minDistance = fitDist * 0.3;
  controls.maxDistance = fitDist * 10;
  controls.update();

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
  scene.add(ambientLight);

  // Visualize routes and vehicles
  visualizeRoutes(routes, scene);
  let vehicleMarkers = createVehicleMarkers(routes, scene);

  // Handle window resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    controls.update();
  });

  // --- Animation control ---
  let animationActive = false;
  const animateBtn = document.getElementById('animateBtn');
  if (animateBtn) {
    animateBtn.addEventListener('click', () => {
      animationActive = !animationActive;
      animateBtn.textContent = animationActive ? 'Pause Animation' : 'Start Animation';
    });
  }

  // --- Animation loop for vehicle movement ---
  const speed = 2.5; // Units per second (adjust for faster/slower animation)
  let lastTime = performance.now();
  function animate() {
    requestAnimationFrame(animate);
    const now = performance.now();
    const delta = (now - lastTime) / 1000; // seconds
    lastTime = now;
    // Animate vehicles only if animationActive
    if (animationActive) {
      vehicleMarkers.forEach(vm => {
        if (!vm.route || vm.route.length < 2) return;
        let currIdx = vm.routeIndex;
        let nextIdx = currIdx + 1;
        if (nextIdx >= vm.route.length) return; // End of route
        const curr = vm.route[currIdx].location;
        const next = vm.route[nextIdx].location;
        // Compute distance between stops
        const dx = next[0] - curr[0];
        const dy = next[1] - curr[1];
        const dist = Math.sqrt(dx * dx + dy * dy);
        // Move t from 0 to 1 based on speed and distance
        vm.t += (speed * delta) / dist;
        if (vm.t >= 1) {
          // Arrived at next stop
          vm.t = 0;
          vm.routeIndex++;
          if (vm.routeIndex >= vm.route.length - 1) {
            // Optionally: loop back to start or stop
            vm.routeIndex = 0; // Uncomment to loop
            // return; // Uncomment to stop at end
          }
        }
        // Interpolate position
        const interpX = curr[0] + (next[0] - curr[0]) * vm.t;
        const interpY = curr[1] + (next[1] - curr[1]) * vm.t;
        vm.marker.position.set(interpX, interpY, 1.5);
      });
    }
    controls.update();
    renderer.render(scene, camera);
  }
  animate();
}

main();
