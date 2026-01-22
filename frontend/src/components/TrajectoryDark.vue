<template>
  <section class="landing-dark">
    <!-- Background Toggle Button -->
    <div class="theme-toggle-wrapper">
      <button @click="toggleTheme" class="theme-toggle-btn" :title="themeStore.isDark ? '切换到浅色' : '切换到深色'">
        <svg v-if="themeStore.isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>

    <!-- Navigation -->
    <nav class="landing-nav">
      <div class="nav-brand">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="3"/>
          <line x1="12" y1="2" x2="12" y2="5"/>
          <line x1="12" y1="19" x2="12" y2="22"/>
          <line x1="4.93" y1="4.93" x2="7.05" y2="7.05"/>
          <line x1="16.95" y1="16.95" x2="19.07" y2="19.07"/>
        </svg>
        <span>RFTIP</span>
      </div>
      <div class="nav-links">
        <a href="#" class="nav-link">功能</a>
        <a href="#" class="nav-link">关于</a>
        <a href="#" class="nav-link">联系</a>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="landing-main">
      <!-- Left Side - Content -->
      <div class="landing-left">
        <div class="content-wrapper">
          <div class="badge">
            <span class="badge-dot"></span>
            <span>雷达频率追踪情报平台</span>
          </div>

          <h1 class="hero-title">
            <span class="title-line">全球雷达</span>
            <span class="title-line highlight">实时追踪</span>
            <span class="title-line">智能分析</span>
          </h1>

          <p class="hero-description">
            RFTIP 是一个先进的雷达频率追踪情报平台，提供实时目标监控、智能轨迹分析和全球数据可视化。支持多源数据融合，为空中交通管理提供全面的决策支持。
          </p>

          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M2 12h5l3-9 4 18 3-9h5"/>
                </svg>
              </div>
              <div>
                <div class="feature-title">轨迹去噪优化</div>
                <div class="feature-desc">智能算法过滤杂波信号</div>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 6v6l4 2"/>
                </svg>
              </div>
              <div>
                <div class="feature-title">自适应误差校准</div>
                <div class="feature-desc">实时修正系统偏差</div>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="2" y1="12" x2="22" y2="12"/>
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
              </div>
              <div>
                <div class="feature-title">地理信息增强</div>
                <div class="feature-desc">高精度地形融合显示</div>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <div>
                <div class="feature-title">大模型意图识别</div>
                <div class="feature-desc">AI分析飞行目标行为</div>
              </div>
            </div>
          </div>

          <div class="cta-group">
            <button class="cta-primary">
              开始使用
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </button>
            <button class="cta-secondary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              观看演示
            </button>
          </div>

          <div class="stats-row">
            <div class="stat-item">
              <div class="stat-number">8+</div>
              <div class="stat-text">雷达站</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">500+</div>
              <div class="stat-text">日追踪</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <div class="stat-number">99.9%</div>
              <div class="stat-text">准确率</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - 3D Visualization -->
      <div class="landing-right">
        <canvas ref="canvasRef" class="radar-canvas"></canvas>
        <div class="canvas-overlay">
          <div class="overlay-tip">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
            </svg>
            <span>拖动旋转 · 滚轮缩放</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll Indicator -->
    <div class="scroll-indicator">
      <div class="scroll-mouse">
        <div class="scroll-wheel"></div>
      </div>
      <div class="scroll-text">向下滚动探索更多</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { useThemeStore } from '@/stores/theme'

const canvasRef = ref<HTMLCanvasElement>()
const themeStore = useThemeStore()

function toggleTheme() {
  themeStore.toggleTheme()
}

// Three.js variables
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animationId: number
let earthGroup: THREE.Group
let radarStations: THREE.Mesh[] = []
let flightPaths: THREE.Line[] = []
let aircraftList: { mesh: THREE.Mesh; path: THREE.Vector3[]; progress: number; speed: number }[] = []
let targetRotationX = 0
let targetRotationY = 0
let isDragging = false
let previousMousePosition = { x: 0, y: 0 }
let textureLoader: THREE.TextureLoader

// Real earth texture URLs
const EARTH_TEXTURE_URL = 'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg'
const EARTH_BUMP_URL = 'https://unpkg.com/three-globe/example/img/earth-topology.png'

function init() {
  if (!canvasRef.value) return

  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(60, (window.innerWidth / 2) / window.innerHeight, 0.1, 1000)
  camera.position.z = 25

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true
  })
  renderer.setSize(window.innerWidth / 2, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setClearColor(0x000000, 0)

  createRadarVisualization()

  animate()

  // Event listeners
  const canvas = canvasRef.value
  canvas.addEventListener('mousedown', onMouseDown)
  canvas.addEventListener('mousemove', onMouseMove)
  canvas.addEventListener('mouseup', onMouseUp)
  canvas.addEventListener('mouseleave', onMouseUp)
  canvas.addEventListener('wheel', onWheel)
  window.addEventListener('resize', handleResize)
}

function createRadarVisualization() {
  // Create earth group
  earthGroup = new THREE.Group()
  scene.add(earthGroup)

  const earthRadius = 8

  // Create texture loader
  textureLoader = new THREE.TextureLoader()

  // Load real earth texture
  textureLoader.load(
    EARTH_TEXTURE_URL,
    (texture) => {
      // On load success
      createEarthWithTexture(texture, earthRadius)
    },
    undefined,
    (error) => {
      // On error, fallback to procedural texture
      console.warn('Failed to load earth texture, using fallback:', error)
      createProceduralEarth(earthRadius)
    }
  )
}

function createEarthWithTexture(texture: THREE.Texture, earthRadius: number) {
  // Base earth with real texture
  const earthGeometry = new THREE.SphereGeometry(earthRadius, 64, 64)
  const earthMaterial = new THREE.MeshPhongMaterial({
    map: texture,
    bumpScale: 0.05,
    specular: new THREE.Color(0x333333),
    shininess: 5
  })
  const earth = new THREE.Mesh(earthGeometry, earthMaterial)
  earthGroup.add(earth)

  // Add lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 10)
  scene.add(directionalLight)

  // Add elements after texture is loaded
  addRadarStationsAndFlights(earthRadius)
}

function createProceduralEarth(earthRadius: number) {
  // Fallback: Create simple colored earth
  const earthGeometry = new THREE.SphereGeometry(earthRadius, 64, 64)
  const earthMaterial = new THREE.MeshPhongMaterial({
    color: 0x1a3a5f,
    emissive: 0x0a1520,
    specular: 0x111111,
    shininess: 10
  })
  const earth = new THREE.Mesh(earthGeometry, earthMaterial)
  earthGroup.add(earth)

  // Add lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(10, 10, 10)
  scene.add(directionalLight)

  addRadarStationsAndFlights(earthRadius)
}

function addRadarStationsAndFlights(earthRadius: number) {
  // Radar stations
  const stationPositions = [
    { lat: 31.23, lon: 121.47, name: 'Shanghai' },
    { lat: 39.90, lon: 116.40, name: 'Beijing' },
    { lat: 23.13, lon: 113.26, name: 'Guangzhou' },
    { lat: 30.57, lon: 104.07, name: 'Chengdu' },
    { lat: 43.83, lon: 87.62, name: 'Urumqi' },
    { lat: 45.80, lon: 126.54, name: 'Harbin' },
    { lat: 22.32, lon: 114.17, name: 'Hong Kong' },
    { lat: 25.03, lon: 121.50, name: 'Taipei' },
    { lat: 35.68, lon: 139.76, name: 'Tokyo' },
    { lat: 37.56, lon: 126.97, name: 'Seoul' },
    { lat: 1.35, lon: 103.81, name: 'Singapore' },
    { lat: 13.75, lon: 100.50, name: 'Bangkok' }
  ]

  stationPositions.forEach(pos => {
    const phi = (90 - pos.lat) * (Math.PI / 180)
    const theta = (pos.lon + 180) * (Math.PI / 180)

    const x = -earthRadius * Math.sin(phi) * Math.cos(theta)
    const y = earthRadius * Math.cos(phi)
    const z = earthRadius * Math.sin(phi) * Math.sin(theta)

    // Radar station marker
    const stationGeometry = new THREE.SphereGeometry(0.2, 16, 16)
    const stationMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 1
    })
    const station = new THREE.Mesh(stationGeometry, stationMaterial)
    station.position.set(x, y, z)
    earthGroup.add(station)
    radarStations.push(station)

    // Pulsing ring around station
    const ringGeometry = new THREE.RingGeometry(0.25, 0.35, 32)
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: 0x06b6d4,
      transparent: true,
      opacity: 0.5,
      side: THREE.DoubleSide
    })
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.copy(station.position)
    ring.lookAt(0, 0, 0)
    ring.userData.originalScale = 1
    ring.userData.pulseSpeed = 0.02 + Math.random() * 0.02
    earthGroup.add(ring)
  })

  // Flight paths with aircraft
  const flightRoutes = [
    { from: 0, to: 3 },   // Shanghai to Chengdu
    { from: 1, to: 4 },   // Beijing to Urumqi
    { from: 2, to: 6 },   // Guangzhou to Hong Kong
    { from: 3, to: 5 },   // Chengdu to Harbin
    { from: 1, to: 2 },   // Beijing to Guangzhou
    { from: 0, to: 7 },   // Shanghai to Taipei
    { from: 1, to: 8 },   // Beijing to Tokyo
    { from: 1, to: 9 },   // Beijing to Seoul
    { from: 6, to: 10 },  // Hong Kong to Singapore
    { from: 2, to: 11 }   // Guangzhou to Bangkok
  ]

  flightRoutes.forEach((route, index) => {
    const fromPos = stationPositions[route.from]
    const toPos = stationPositions[route.to]

    // Create curved flight path (great circle)
    const pathPoints = createGreatCirclePath(fromPos, toPos, earthRadius + 1.5)

    // Draw flight path as line
    const pathGeometry = new THREE.BufferGeometry().setFromPoints(pathPoints)
    const pathMaterial = new THREE.LineBasicMaterial({
      color: 0x8b5cf6,
      transparent: true,
      opacity: 0.4
    })
    const pathLine = new THREE.Line(pathGeometry, pathMaterial)
    earthGroup.add(pathLine)
    flightPaths.push(pathLine)

    // Create aircraft on this path
    const aircraftGeom = new THREE.ConeGeometry(0.12, 0.4, 8)
    aircraftGeom.rotateX(Math.PI / 2)
    const aircraftMat = new THREE.MeshBasicMaterial({
      color: 0xa855f7,
      transparent: true,
      opacity: 1
    })
    const aircraft = new THREE.Mesh(aircraftGeom, aircraftMat)

    const startPos = pathPoints[0]
    aircraft.position.copy(startPos)

    earthGroup.add(aircraft)

    aircraftList.push({
      mesh: aircraft,
      path: pathPoints,
      progress: Math.random(),
      speed: 0.002 + Math.random() * 0.003
    })
  })
}

// Create great circle path between two lat/lon points
function createGreatCirclePath(from: { lat: number; lon: number }, to: { lat: number; lon: number }, altitude: number, segments = 50): THREE.Vector3[] {
  const points: THREE.Vector3[] = []

  const phi1 = (90 - from.lat) * (Math.PI / 180)
  const theta1 = (from.lon + 180) * (Math.PI / 180)
  const phi2 = (90 - to.lat) * (Math.PI / 180)
  const theta2 = (to.lon + 180) * (Math.PI / 180)

  const x1 = -Math.sin(phi1) * Math.cos(theta1)
  const y1 = Math.cos(phi1)
  const z1 = Math.sin(phi1) * Math.sin(theta1)

  const x2 = -Math.sin(phi2) * Math.cos(theta2)
  const y2 = Math.cos(phi2)
  const z2 = Math.sin(phi2) * Math.sin(theta2)

  // Calculate angle between points
  const dot = x1 * x2 + y1 * y2 + z1 * z2
  const angle = Math.acos(Math.max(-1, Math.min(1, dot)))

  for (let i = 0; i <= segments; i++) {
    const t = i / segments
    const theta = angle * t

    // Spherical interpolation (slerp)
    let x, y, z
    if (angle < 0.001) {
      x = x1
      y = y1
      z = z1
    } else {
      const sinAngle = Math.sin(angle)
      const a = Math.sin((1 - t) * angle) / sinAngle
      const b = Math.sin(t * angle) / sinAngle
      x = a * x1 + b * x2
      y = a * y1 + b * y2
      z = a * z1 + b * z2

      // Normalize and add altitude
      const len = Math.sqrt(x * x + y * y + z * z)
      x = x / len * altitude
      y = y / len * altitude
      z = z / len * altitude
    }

    points.push(new THREE.Vector3(x, y, z))
  }

  return points
}

function onMouseDown(event: MouseEvent) {
  isDragging = true
  previousMousePosition = { x: event.clientX, y: event.clientY }
}

function onMouseMove(event: MouseEvent) {
  if (!isDragging) return

  const deltaX = event.clientX - previousMousePosition.x
  const deltaY = event.clientY - previousMousePosition.y

  targetRotationY += deltaX * 0.005
  targetRotationX += deltaY * 0.005

  previousMousePosition = { x: event.clientX, y: event.clientY }
}

function onMouseUp() {
  isDragging = false
}

function onWheel(event: WheelEvent) {
  camera.position.z += event.deltaY * 0.01
  camera.position.z = Math.max(15, Math.min(40, camera.position.z))
}

function handleResize() {
  if (!camera || !renderer) return
  camera.aspect = (window.innerWidth / 2) / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth / 2, window.innerHeight)
}

function animate() {
  animationId = requestAnimationFrame(animate)

  // Smooth rotation of earth group (only responds to user input)
  earthGroup.rotation.y += (targetRotationY - earthGroup.rotation.y) * 0.05
  earthGroup.rotation.x += (targetRotationX - earthGroup.rotation.x) * 0.05

  // Animate aircraft along their paths
  aircraftList.forEach(aircraft => {
    aircraft.progress += aircraft.speed
    if (aircraft.progress >= 1) {
      aircraft.progress = 0
    }

    const pathIndex = Math.floor(aircraft.progress * (aircraft.path.length - 1))
    const nextPathIndex = Math.min(pathIndex + 1, aircraft.path.length - 1)
    const t = (aircraft.progress * (aircraft.path.length - 1)) - pathIndex

    const currentPos = aircraft.path[pathIndex]
    const nextPos = aircraft.path[nextPathIndex]

    // Interpolate position
    aircraft.mesh.position.lerpVectors(currentPos, nextPos, t)

    // Make aircraft look at next point
    const lookAtPos = nextPos.clone()
    aircraft.mesh.lookAt(lookAtPos)
  })

  // Animate radar station rings
  earthGroup.children.forEach((child) => {
    if (child instanceof THREE.Mesh && child.geometry.type === 'RingGeometry' && child.userData.originalScale) {
      const time = Date.now() * 0.001
      const pulse = Math.sin(time * 3) * 0.3 + 1
      child.scale.set(pulse, pulse, pulse)
      child.material.opacity = 0.5 - (pulse - 1) * 0.3
    }
  })

  renderer.render(scene, camera)
}

onMounted(() => {
  init()
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.landing-dark {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  overflow: hidden;
}

/* Theme Toggle Button */
.theme-toggle-wrapper {
  position: fixed;
  top: 2rem;
  right: 2rem;
  z-index: 100;
}

.theme-toggle-btn {
  width: 3rem;
  height: 3rem;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #06b6d4;
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-toggle-btn:hover {
  background: rgba(30, 41, 59, 1);
  border-color: #06b6d4;
  transform: scale(1.1);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
}

.theme-toggle-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Navigation */
.landing-nav {
  position: fixed;
  top: 2rem;
  left: 2rem;
  right: 8rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 50;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #f8fafc;
  font-weight: 700;
  font-size: 1.25rem;
}

.nav-brand svg {
  width: 2rem;
  height: 2rem;
  color: #06b6d4;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #06b6d4;
}

/* Main Content */
.landing-main {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  min-height: 100vh;
  padding: 8rem 4rem 4rem;
  max-width: 1600px;
  margin: 0 auto;
}

/* Left Side */
.landing-left {
  display: flex;
  align-items: center;
}

.content-wrapper {
  max-width: 600px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(6, 182, 212, 0.1);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 2rem;
  font-size: 0.75rem;
  color: #06b6d4;
  font-weight: 600;
  letter-spacing: 0.1em;
  margin-bottom: 2rem;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: #06b6d4;
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.hero-title {
  font-size: 4rem;
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: 1.5rem;
}

.title-line {
  display: block;
  color: #f8fafc;
}

.title-line.highlight {
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.125rem;
  line-height: 1.7;
  color: #94a3b8;
  margin-bottom: 2.5rem;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.feature-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%);
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #06b6d4;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 1.25rem;
  height: 1.25rem;
}

.feature-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #f8fafc;
  margin-bottom: 0.125rem;
}

.feature-desc {
  font-size: 0.75rem;
  color: #64748b;
}

/* CTA Buttons */
.cta-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
}

.cta-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  border: none;
  border-radius: 0.75rem;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(6, 182, 212, 0.4);
}

.cta-primary svg {
  width: 1.25rem;
  height: 1.25rem;
}

.cta-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  color: #94a3b8;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cta-secondary:hover {
  border-color: #06b6d4;
  color: #06b6d4;
  background: rgba(6, 182, 212, 0.1);
}

.cta-secondary svg {
  width: 1.25rem;
  height: 1.25rem;
}

/* Stats Row */
.stats-row {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-text {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.stat-divider {
  width: 1px;
  height: 2rem;
  background: rgba(148, 163, 184, 0.2);
}

/* Right Side - 3D Canvas */
.landing-right {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radar-canvas {
  width: 100%;
  height: 600px;
  border-radius: 2rem;
}

.canvas-overlay {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
}

.overlay-tip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 2rem;
  font-size: 0.75rem;
  color: #64748b;
}

.overlay-tip svg {
  width: 1rem;
  height: 1rem;
}

/* Scroll Indicator */
.scroll-indicator {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.scroll-mouse {
  width: 1.5rem;
  height: 2.5rem;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 1.25rem;
  position: relative;
}

.scroll-wheel {
  width: 0.25rem;
  height: 0.5rem;
  background: #06b6d4;
  border-radius: 0.125rem;
  position: absolute;
  top: 0.5rem;
  animation: scroll 2s ease-in-out infinite;
}

@keyframes scroll {
  0% { transform: translateY(0); opacity: 1; }
  100% { transform: translateY(1rem); opacity: 0; }
}

.scroll-text {
  font-size: 0.75rem;
  color: #64748b;
  letter-spacing: 0.1em;
}

/* Responsive */
@media (max-width: 1024px) {
  .landing-main {
    grid-template-columns: 1fr;
    gap: 2rem;
    padding-top: 10rem;
  }

  .landing-right {
    order: -1;
  }

  .radar-canvas {
    height: 400px;
  }

  .hero-title {
    font-size: 3rem;
  }
}

@media (max-width: 768px) {
  .landing-nav {
    left: 1rem;
    right: 5rem;
  }

  .nav-links {
    display: none;
  }

  .landing-main {
    padding: 8rem 1.5rem 2rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .cta-group {
    flex-direction: column;
  }

  .cta-primary,
  .cta-secondary {
    width: 100%;
    justify-content: center;
  }

  .stats-row {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .stat-divider {
    display: none;
  }
}
</style>
