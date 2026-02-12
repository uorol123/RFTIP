<template>
  <div class="globe-container">
    <canvas ref="canvasEl"></canvas>
    <div class="ui-overlay">
      <div class="ui-content">
        <div class="ui-badge">
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
          </svg>
          <span>实时雷达追踪系统</span>
        </div>
        <h1 class="ui-title">
          <span class="title-main">RFTIP</span>
          <span class="title-sub">雷达轨迹融合追踪平台</span>
        </h1>
        <p class="ui-desc">
          多雷达站数据融合 · 智能轨迹预测 · 实时预警监控
        </p>
        <div class="ui-stats">
          <div class="stat-card">
            <div class="stat-val">{{ radarStations.length }}</div>
            <div class="stat-label">雷达站</div>
          </div>
          <div class="stat-card">
            <div class="stat-val">{{ flightPaths.length }}</div>
            <div class="stat-label">轨迹路线</div>
          </div>
          <div class="stat-card">
            <div class="stat-val">99.9%</div>
            <div class="stat-label">准确率</div>
          </div>
        </div>
        <button class="ui-btn" @click="goToDashboard">
          <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clip-rule="evenodd"/>
          </svg>
          进入控制台
        </button>
      </div>
    </div>
    <div class="ui-legend">
      <div class="legend-item">
        <span class="dot green"></span>
        <span>雷达站</span>
      </div>
      <div class="legend-item">
        <span class="dot blue"></span>
        <span>轨迹路线</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import * as THREE from 'three'

const router = useRouter()
const canvasEl = ref<HTMLCanvasElement>()

const radarStations = [
  { name: '北京', lat: 39.9042, lng: 116.4074 },
  { name: '上海', lat: 31.2304, lng: 121.4737 },
  { name: '广州', lat: 23.1291, lng: 113.2644 },
  { name: '成都', lat: 30.5728, lng: 104.0668 },
  { name: '深圳', lat: 22.5431, lng: 114.0579 },
  { name: '武汉', lat: 30.5928, lng: 114.3055 },
  { name: '重庆', lat: 29.5630, lng: 106.5516 },
  { name: '西安', lat: 34.3416, lng: 108.9398 },
  { name: '长沙', lat: 28.2282, lng: 112.9388 },
  { name: '南京', lat: 32.0603, lng: 118.7969 },
  { name: '杭州', lat: 30.2741, lng: 120.1551 },
  { name: '天津', lat: 39.3434, lng: 117.3616 },
  { name: '沈阳', lat: 41.8057, lng: 123.4315 },
  { name: '哈尔滨', lat: 45.8038, lng: 126.5340 },
  { name: '乌鲁木齐', lat: 43.8256, lng: 87.6168 },
  { name: '拉萨', lat: 29.6525, lng: 91.1721 },
  { name: '昆明', lat: 25.0389, lng: 102.7183 },
  { name: '海口', lat: 20.0174, lng: 110.3492 },
  { name: '济南', lat: 36.6512, lng: 117.1205 },
  { name: '郑州', lat: 34.7466, lng: 113.6253 }
]

const flightPaths = [
  [0, 1], [0, 2], [0, 4], [0, 5], [0, 7], [0, 11],
  [1, 3], [1, 4], [1, 9], [1, 10],
  [2, 4], [2, 5], [2, 17],
  [3, 4], [3, 7], [3, 16],
  [5, 6], [5, 7], [5, 8],
  [7, 8], [7, 14],
  [9, 10], [9, 12],
  [11, 12], [11, 18],
  [13, 14], [14, 15],
  [15, 16], [16, 17]
]

let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let earthGroup: THREE.Group | null = null
let stars: THREE.Points | null = null
let animationId: number | null = null
let isDragging = false
let prevMouse = { x: 0, y: 0 }

function latLngToVec3(lat: number, lng: number, r: number) {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)
  const x = -r * Math.sin(phi) * Math.cos(theta)
  const y = r * Math.cos(phi)
  const z = r * Math.sin(phi) * Math.sin(theta)
  return new THREE.Vector3(x, y, z)
}

function createEarth(r: number): THREE.Mesh {
  const geo = new THREE.SphereGeometry(r, 64, 64)

  const canvas = document.createElement('canvas')
  canvas.width = 2048
  canvas.height = 1024
  const ctx = canvas.getContext('2d')!

  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height)
  grad.addColorStop(0, '#1a4a6e')
  grad.addColorStop(0.5, '#0d3d5c')
  grad.addColorStop(1, '#0a2d4c')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  const tex = new THREE.CanvasTexture(canvas)

  const mat = new THREE.MeshPhongMaterial({
    map: tex,
    specular: new THREE.Color(0x333333),
    shininess: 5
  })

  return new THREE.Mesh(geo, mat)
}

function createStars(): THREE.Points {
  const geo = new THREE.BufferGeometry()
  const pos: number[] = []

  for (let i = 0; i < 8000; i++) {
    const x = (Math.random() - 0.5) * 1800
    const y = (Math.random() - 0.5) * 1800
    const z = (Math.random() - 0.5) * 1800

    if (Math.sqrt(x*x + y*y + z*z) > 250) {
      pos.push(x, y, z)
    }
  }

  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3))

  const mat = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1.2,
    transparent: true,
    opacity: 0.7
  })

  return new THREE.Points(geo, mat)
}

function createMarker(station: { lat: number, lng: number }, r: number): THREE.Group {
  const group = new THREE.Group()
  const pos = latLngToVec3(station.lat, station.lng, r)
  group.position.copy(pos)
  group.lookAt(new THREE.Vector3(0, 0, 0))

  const core = new THREE.Mesh(
    new THREE.SphereGeometry(1.2, 16, 16),
    new THREE.MeshBasicMaterial({ color: 0x10B981 })
  )
  group.add(core)

  const ring = new THREE.Mesh(
    new THREE.RingGeometry(2, 3.5, 32),
    new THREE.MeshBasicMaterial({ color: 0x10B981, transparent: true, opacity: 0.5, side: THREE.DoubleSide })
  )
  ring.position.z = 0.1
  group.add(ring)

  group.userData.pulse = Math.random() * Math.PI * 2

  return group
}

function createArc(from: { lat: number, lng: number }, to: { lat: number, lng: number }, r: number): THREE.Line {
  const start = latLngToVec3(from.lat, from.lng, r)
  const end = latLngToVec3(to.lat, to.lng, r)

  const dist = start.distanceTo(end)
  const midHeight = Math.min(dist * 0.3, 30)
  const mid = start.clone().add(end).multiplyScalar(0.5)
  mid.normalize().multiplyScalar(r + midHeight)

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
  const pts = curve.getPoints(50)

  const geo = new THREE.BufferGeometry().setFromPoints(pts)
  const mat = new THREE.LineBasicMaterial({ color: 0x3B82F6, transparent: true, opacity: 0.5 })

  return new THREE.Line(geo, mat)
}

function init() {
  if (!canvasEl.value) return

  const w = canvasEl.value.clientWidth
  const h = canvasEl.value.clientHeight

  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x000005)

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000)
  camera.position.z = 220

  renderer = new THREE.WebGLRenderer({ canvas: canvasEl.value, antialias: true })
  renderer.setSize(w, h)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  earthGroup = new THREE.Group()
  scene.add(earthGroup)

  const R = 80

  stars = createStars()
  scene.add(stars)

  const earth = createEarth(R)
  earthGroup.add(earth)

  radarStations.forEach(s => {
    earthGroup.add(createMarker(s, R))
  })

  flightPaths.forEach(p => {
    const from = radarStations[p[0]]
    const to = radarStations[p[1]]
    earthGroup.add(createArc(from, to, R))
  })

  earthGroup.rotation.y = -Math.PI / 6
  earthGroup.rotation.x = Math.PI / 8

  const canvas = canvasEl.value
  canvas.addEventListener('mousedown', e => {
    isDragging = true
    prevMouse = { x: e.clientX, y: e.clientY }
  })

  canvas.addEventListener('mousemove', e => {
    if (!isDragging || !earthGroup) return
    const dx = e.clientX - prevMouse.x
    const dy = e.clientY - prevMouse.y
    earthGroup.rotation.y += dx * 0.005
    earthGroup.rotation.x += dy * 0.005
    prevMouse = { x: e.clientX, y: e.clientY }
  })

  canvas.addEventListener('mouseup', () => isDragging = false)
  canvas.addEventListener('mouseleave', () => isDragging = false)

  canvas.addEventListener('wheel', e => {
    e.preventDefault()
    if (!camera) return
    camera.position.z += e.deltaY * 0.1
    camera.position.z = Math.max(150, Math.min(400, camera.position.z))
  }, { passive: false })

  animate()
}

let time = 0
function animate() {
  animationId = requestAnimationFrame(animate)
  time += 0.016

  if (earthGroup) {
    if (!isDragging) {
      earthGroup.rotation.y += 0.0003
    }

    earthGroup.children.forEach(child => {
      if (child.userData.pulse !== undefined) {
        const s = 1 + Math.sin(time * 2 + child.userData.pulse) * 0.15
        child.scale.setScalar(s)
      }
    })
  }

  if (stars) {
    stars.rotation.y += 0.00002
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

function goToDashboard() {
  router.push('/dashboard')
}

onMounted(() => {
  init()
  window.addEventListener('resize', () => {
    if (!camera || !canvasEl.value || !renderer) return
    const w = canvasEl.value.clientWidth
    const h = canvasEl.value.clientHeight
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  })
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) renderer.dispose()
})
</script>

<style scoped>
.globe-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(ellipse at center, #0a0e1a 0%, #000005 100%);
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  cursor: grab;
}

canvas:active {
  cursor: grabbing;
}

.ui-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  pointer-events: none;
  z-index: 10;
}

.ui-content {
  padding: 0 4rem;
  max-width: 600px;
  pointer-events: auto;
}

.ui-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 2rem;
  color: #60a5fa;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.ui-title {
  margin-bottom: 1rem;
}

.title-main {
  display: block;
  font-size: 4rem;
  font-weight: 800;
  background: linear-gradient(135deg, #60a5fa 0%, #34d399 50%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.title-sub {
  display: block;
  font-size: 1.5rem;
  color: #e2e8f0;
  font-weight: 600;
  margin-top: 0.5rem;
}

.ui-desc {
  color: #94a3b8;
  font-size: 1.0625rem;
  line-height: 1.7;
  margin-bottom: 2.5rem;
}

.ui-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  padding: 1rem 1.5rem;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1rem;
  text-align: center;
  min-width: 100px;
}

.stat-val {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
}

.stat-label {
  font-size: 0.8125rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.ui-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
}

.ui-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(59, 130, 246, 0.5);
}

.ui-legend {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #cbd5e1;
  font-size: 0.875rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.green { background: #10B981; }
.dot.blue { background: #3B82F6; }

@media (max-width: 768px) {
  .ui-content {
    padding: 0 1.5rem;
  }

  .title-main {
    font-size: 2.5rem;
  }

  .title-sub {
    font-size: 1.125rem;
  }

  .ui-stats {
    flex-wrap: wrap;
    gap: 1rem;
  }

  .stat-card {
    min-width: 80px;
    padding: 0.75rem 1rem;
  }

  .ui-legend {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
