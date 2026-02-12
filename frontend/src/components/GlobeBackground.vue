<template>
  <div ref="containerRef" class="globe-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

const containerRef = ref<HTMLDivElement>()

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let globe: THREE.Mesh
let glowMesh: THREE.Mesh
let stars: THREE.Points
let animationId: number
let isDragging = false
let previousMousePosition = { x: 0, y: 0 }
let targetRotationY = 0
let currentRotationY = 0

// 中国雷达站坐标
const radarStations = [
  { name: '北京', lat: 39.9042, lng: 116.4074 },
  { name: '上海', lat: 31.2304, lng: 121.4737 },
  { name: '广州', lat: 23.1291, lng: 113.2644 },
  { name: '成都', lat: 30.5728, lng: 104.0668 },
  { name: '深圳', lat: 22.5431, lng: 114.0579 },
  { name: '武汉', lat: 30.5928, lng: 114.3055 },
  { name: '西安', lat: 34.3416, lng: 108.9398 },
  { name: '哈尔滨', lat: 45.8038, lng: 126.5350 },
  { name: '乌鲁木齐', lat: 43.8256, lng: 87.6168 },
  { name: '拉萨', lat: 29.6500, lng: 91.1000 },
]

// 航线连接
const flightPaths = [
  [0, 1], [0, 2], [0, 5], [0, 6], [0, 7],
  [1, 2], [1, 3], [1, 4],
  [2, 4], [2, 5],
  [3, 5], [3, 6], [3, 9],
  [5, 6], [6, 7], [6, 8],
  [8, 9]
]

// 经纬度转3D坐标
function latLngToVector3(lat: number, lng: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180)
  const theta = (lng + 180) * (Math.PI / 180)
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  )
}

// 创建星空背景
function createStars(): THREE.Points {
  const geometry = new THREE.BufferGeometry()
  const vertices: number[] = []

  for (let i = 0; i < 3000; i++) {
    const x = (Math.random() - 0.5) * 2000
    const y = (Math.random() - 0.5) * 2000
    const z = (Math.random() - 0.5) * 2000
    vertices.push(x, y, z)
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3))

  const material = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 1,
    transparent: true,
    opacity: 0.8,
    sizeAttenuation: true
  })

  return new THREE.Points(geometry, material)
}

// 创建地球辉光
function createGlow(radius: number): THREE.Mesh {
  const geometry = new THREE.SphereGeometry(radius * 1.15, 64, 64)
  const material = new THREE.ShaderMaterial({
    uniforms: {
      c: { value: 0.4 },
      p: { value: 4.0 },
      glowColor: { value: new THREE.Color(0x3b82f6) },
      viewVector: { value: new THREE.Vector3() }
    },
    vertexShader: `
      uniform vec3 viewVector;
      varying float intensity;
      void main() {
        vec3 vNormal = normalize(normalMatrix * normal);
        vec3 vNormel = normalize(normalMatrix * viewVector);
        intensity = pow(0.65 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 glowColor;
      uniform float c;
      uniform float p;
      varying float intensity;
      void main() {
        vec3 glow = glowColor * c * intensity;
        gl_FragColor = vec4(glow, intensity * 0.6);
      }
    `,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    transparent: true
  })

  return new THREE.Mesh(geometry, material)
}

// 创建弧线
function createArc(start: THREE.Vector3, end: THREE.Vector3, globeRadius: number): THREE.Line {
  const distance = start.distanceTo(end)
  const arcHeight = distance * 0.25

  const mid = start.clone().add(end).multiplyScalar(0.5)
  mid.normalize().multiplyScalar(globeRadius + arcHeight)

  const curve = new THREE.QuadraticBezierCurve3(start, mid, end)
  const points = curve.getPoints(50)

  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const material = new THREE.LineBasicMaterial({
    color: 0x60a5fa,
    transparent: true,
    opacity: 0.4
  })

  return new THREE.Line(geometry, material)
}

// 创建雷达站点
function createStation(position: THREE.Vector3): THREE.Group {
  const group = new THREE.Group()

  // 核心点
  const coreGeometry = new THREE.SphereGeometry(0.8, 16, 16)
  const coreMaterial = new THREE.MeshBasicMaterial({ color: 0x10b981 })
  const core = new THREE.Mesh(coreGeometry, coreMaterial)
  core.position.copy(position)
  group.add(core)

  // 外圈
  const ringGeometry = new THREE.RingGeometry(1.2, 1.6, 32)
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0x10b981,
    transparent: true,
    opacity: 0.6,
    side: THREE.DoubleSide
  })
  const ring = new THREE.Mesh(ringGeometry, ringMaterial)
  ring.position.copy(position)
  ring.lookAt(0, 0, 0)
  group.add(ring)

  return group
}

function init() {
  if (!containerRef.value) return

  const container = containerRef.value
  const width = container.clientWidth
  const height = container.clientHeight

  // 场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x030712)

  // 相机
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 2000)
  camera.position.z = 300

  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  container.appendChild(renderer.domElement)

  // 星空
  stars = createStars()
  scene.add(stars)

  // 地球
  const globeRadius = 100
  const textureLoader = new THREE.TextureLoader()

  // 使用真实地球纹理
  const earthTexture = textureLoader.load('/earth-night.jpg')
  const bumpTexture = textureLoader.load('/earth-topology.png')

  const globeGeometry = new THREE.SphereGeometry(globeRadius, 64, 64)
  const globeMaterial = new THREE.MeshPhongMaterial({
    map: earthTexture,
    bumpMap: bumpTexture,
    bumpScale: 0.5,
    specular: new THREE.Color(0x333333),
    shininess: 5
  })

  globe = new THREE.Mesh(globeGeometry, globeMaterial)
  scene.add(globe)

  // 辉光
  glowMesh = createGlow(globeRadius)
  scene.add(glowMesh)

  // 雷达站和航线
  const stationsGroup = new THREE.Group()

  radarStations.forEach(station => {
    const pos = latLngToVector3(station.lat, station.lng, globeRadius)
    const stationMesh = createStation(pos)
    stationsGroup.add(stationMesh)
  })

  flightPaths.forEach(([i, j]) => {
    const start = latLngToVector3(radarStations[i].lat, radarStations[i].lng, globeRadius)
    const end = latLngToVector3(radarStations[j].lat, radarStations[j].lng, globeRadius)
    const arc = createArc(start, end, globeRadius)
    stationsGroup.add(arc)
  })

  scene.add(stationsGroup)

  // 光照
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.2)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
  directionalLight.position.set(5, 3, 5)
  scene.add(directionalLight)

  // 初始旋转 - 聚焦中国
  globe.rotation.y = -Math.PI / 2
  stationsGroup.rotation.y = -Math.PI / 2
  targetRotationY = -Math.PI / 2
  currentRotationY = -Math.PI / 2

  // 将站点组附加到地球
  globe.add(stationsGroup)
  stationsGroup.rotation.y = 0

  // 事件监听
  setupEvents()

  // 开始动画
  animate()
}

function setupEvents() {
  const canvas = renderer.domElement

  canvas.addEventListener('mousedown', (e) => {
    isDragging = true
    previousMousePosition = { x: e.clientX, y: e.clientY }
  })

  canvas.addEventListener('mousemove', (e) => {
    if (!isDragging) return
    const deltaX = e.clientX - previousMousePosition.x
    targetRotationY += deltaX * 0.005
    previousMousePosition = { x: e.clientX, y: e.clientY }
  })

  canvas.addEventListener('mouseup', () => { isDragging = false })
  canvas.addEventListener('mouseleave', () => { isDragging = false })

  // 触摸支持
  canvas.addEventListener('touchstart', (e) => {
    isDragging = true
    previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY }
  })

  canvas.addEventListener('touchmove', (e) => {
    if (!isDragging) return
    const deltaX = e.touches[0].clientX - previousMousePosition.x
    targetRotationY += deltaX * 0.005
    previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY }
  })

  canvas.addEventListener('touchend', () => { isDragging = false })

  window.addEventListener('resize', onResize)
}

function animate() {
  animationId = requestAnimationFrame(animate)

  // 自动旋转
  if (!isDragging) {
    targetRotationY += 0.001
  }

  // 平滑旋转
  currentRotationY += (targetRotationY - currentRotationY) * 0.05
  globe.rotation.y = currentRotationY

  // 星空缓慢旋转
  stars.rotation.y += 0.0001

  renderer.render(scene, camera)
}

function onResize() {
  if (!containerRef.value) return

  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

onMounted(() => {
  init()
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  if (animationId) cancelAnimationFrame(animationId)
  if (renderer) {
    renderer.dispose()
    containerRef.value?.removeChild(renderer.domElement)
  }
})
</script>

<style scoped>
.globe-container {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.globe-container canvas {
  cursor: grab;
}

.globe-container canvas:active {
  cursor: grabbing;
}
</style>
