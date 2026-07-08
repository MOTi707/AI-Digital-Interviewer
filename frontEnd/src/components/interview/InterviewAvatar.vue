<template>
  <div class="relative flex items-center justify-center w-full flex-1 min-h-0">
    <div
      ref="containerRef"
      class="w-full border-4 border-black relative overflow-hidden bg-[#fef9ef] shadow-[5px_5px_0px_0px_rgba(0,0,0,1)]"
      style="height: 100%;"
    >
      <canvas ref="canvasRef" class="w-full h-full block transition-opacity duration-500" :class="isLoading ? 'opacity-0' : 'opacity-100'" />
      <!-- 模型加载中提示 -->
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-[#fef9ef] z-10">
        <div class="text-center p-4">
          <div class="text-4xl mb-2 animate-pulse">🎭</div>
          <div class="font-black text-sm mb-1">加载面试官中...</div>
        </div>
      </div>
      <!-- 模型加载失败提示 -->
      <div v-if="loadError" class="absolute inset-0 flex items-center justify-center bg-[#fef9ef]">
        <div class="text-center p-4">
          <div class="text-4xl mb-2">🎭</div>
          <div class="font-black text-sm mb-1">VRM 模型未找到</div>
          <div class="font-sans text-xs text-gray-600">
            请将 .vrm 模型文件放到<br/>public/models/avatar.vrm
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRMUtils, VRMExpressionPresetName, VRMHumanBoneName } from '@pixiv/three-vrm'
import type { VRM } from '@pixiv/three-vrm'

// ── 类型定义 ──
type AvatarState = 'idle' | 'thinking' | 'satisfied' | 'probing'
type Mood = 'neutral' | 'happy' | 'angry' | 'sad' | 'relaxed' | 'surprised'

const props = defineProps<{
  speaking: boolean
  avatarState?: AvatarState
  inputFocused?: boolean
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
const loadError = ref(false)
const isLoading = ref(true)

let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let controls: OrbitControls | null = null
let vrm: VRM | null = null
let animationId: number | null = null
let resizeObserver: ResizeObserver | null = null
let clock: THREE.Clock | null = null
let isSpeaking = false

// ── 表情系统 ──
let currentMood: Mood = 'neutral' // eslint-disable-line
let targetMood: Mood = 'neutral' // eslint-disable-line
let moodTransition = 0 // eslint-disable-line
const moodWeights: Record<Mood, number> = {
  neutral: 1, happy: 0, angry: 0, sad: 0, relaxed: 0, surprised: 0
}
const targetMoodWeights: Record<Mood, number> = {
  neutral: 1, happy: 0, angry: 0, sad: 0, relaxed: 0, surprised: 0
}

// ── 视线系统 ──
let lookAtMode: 'camera' | 'mouse' | 'input' = 'camera'
const mouseNDC = new THREE.Vector2(0, 0) // 归一化设备坐标
const lookAtTargetPos = new THREE.Vector3(0, 1.15, 1.8) // 默认看摄像头
const inputLookAtPos = new THREE.Vector3(0.5, 0.8, 1.5) // 看输入区域的位置
let mouseInCanvas = false

// ── 口型动画 ──
let currentMouthShape = 'aa'
let mouthTimer = 0
let mouthInterval = 0.15
let mouthWeight = 0

// ── 眨眼状态 ──
let blinkTimer = 0
let nextBlinkTime = 3
let isBlinking = false
let blinkProgress = 0

// ── 状态动画 ──
let currentState: AvatarState = 'idle'
let stateTimer = 0
let baseArmRotation = 1.22 // 普通模型的基础手臂旋转值
let forearmRotation = -0.1 // 普通模型的前臂旋转值

// ── watch props ──
watch(() => props.speaking, (val) => {
  isSpeaking = val
  if (val) {
    mouthTimer = 0
    mouthInterval = 0.1 + Math.random() * 0.1
  }
})

watch(() => props.avatarState, (val) => {
  if (val && val !== currentState) {
    currentState = val
    stateTimer = 0
  }
})

watch(() => props.inputFocused, (focused) => {
  if (focused) {
    // 输入框聚焦时视线回到摄像头
    lookAtMode = 'camera'
  }
})

const MOUTH_SHAPES = ['aa', 'ih', 'ou', 'ee', 'oh'] as const

// ── 鼠标事件（监听整个窗口）──
function onMouseMove(e: MouseEvent) {
  // 输入框聚焦时不跟踪鼠标
  if (props.inputFocused) return
  // 使用整个窗口尺寸计算归一化坐标
  mouseNDC.x = (e.clientX / window.innerWidth) * 2 - 1
  mouseNDC.y = -(e.clientY / window.innerHeight) * 2 + 1
  mouseInCanvas = true

  // 鼠标移动时自动切换视线模式
  if (lookAtMode === 'camera') {
    lookAtMode = 'mouse'
  }
}

function onMouseLeave() {
  mouseInCanvas = false
  // 鼠标离开窗口后回到摄像头视线
  if (lookAtMode === 'mouse') {
    lookAtMode = 'camera'
  }
}

// ── expose 方法 ──
function setMood(mood: Mood, duration = 2000) {
  targetMood = mood
  moodTransition = 0
  // 设置目标权重
  for (const key of Object.keys(targetMoodWeights) as Mood[]) {
    targetMoodWeights[key] = key === mood ? 1 : 0
  }
  // 自动回到 neutral
  if (mood !== 'neutral' && duration > 0) {
    setTimeout(() => {
      targetMood = 'neutral'
      moodTransition = 0
      for (const key of Object.keys(targetMoodWeights) as Mood[]) {
        targetMoodWeights[key] = key === 'neutral' ? 1 : 0
      }
    }, duration)
  }
}

function lookAtInput() {
  lookAtMode = 'input'
  // 3秒后回到摄像头
  setTimeout(() => {
    if (lookAtMode === 'input') {
      lookAtMode = mouseInCanvas ? 'mouse' : 'camera'
    }
  }, 3000)
}

function switchModel(url: string) {
  // 移除旧模型
  if (vrm) {
    if (vrm.lookAt && (vrm.lookAt as any).__helper) {
      scene?.remove((vrm.lookAt as any).__helper)
      ;(vrm.lookAt as any).__helper = null
    }
    scene?.remove(vrm.scene)
    vrm.scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
    vrm = null
  }
  // 重置状态
  currentMood = 'neutral'
  targetMood = 'neutral'
  for (const key of Object.keys(moodWeights) as Mood[]) {
    moodWeights[key] = key === 'neutral' ? 1 : 0
    targetMoodWeights[key] = key === 'neutral' ? 1 : 0
  }
  lookAtMode = 'camera'
  currentState = 'idle'
  // 加载新模型
  loadVRM(url)
}

defineExpose({ setMood, lookAtInput, switchModel })

// ── Three.js 初始化 ──

function initThree() {
  const canvas = canvasRef.value
  if (!canvas) return
  const container = containerRef.value
  if (!container) return
  const width = container.clientWidth
  const height = container.clientHeight

  clock = new THREE.Clock()
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xfef9ef)

  camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 100)
  camera.position.set(0, 1.05, 1.8)

  renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2

  // 灯光
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
  scene.add(ambientLight)
  const mainLight = new THREE.DirectionalLight(0xffffff, 1.5)
  mainLight.position.set(2, 3, 2)
  mainLight.castShadow = true
  scene.add(mainLight)
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.5)
  fillLight.position.set(-2, 2, -1)
  scene.add(fillLight)
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.3)
  rimLight.position.set(0, 1, -3)
  scene.add(rimLight)

  // 控制器
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableZoom = false
  controls.enablePan = false
  controls.autoRotate = false
  controls.target.set(0, 0.95, 0)
  controls.minPolarAngle = Math.PI * 0.3
  controls.maxPolarAngle = Math.PI * 0.6
  controls.update()

  // ResizeObserver
  resizeObserver = new ResizeObserver(() => {
    if (!containerRef.value || !renderer || !camera) return
    const w = containerRef.value.clientWidth
    const h = containerRef.value.clientHeight
    if (w > 0 && h > 0) {
      renderer.setSize(w, h)
      camera.aspect = w / h
      camera.updateProjectionMatrix()
    }
  })
  if (containerRef.value) {
    resizeObserver.observe(containerRef.value)
  }

  loadVRM()
  animate()
}

function fixTPose(vrmModel: VRM) {
  if (!vrmModel.humanoid) return
  const rightUpperArm = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightUpperArm)
  const leftUpperArm = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftUpperArm)
  const rightLowerArm = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightLowerArm)
  const leftLowerArm = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftLowerArm)
  const rightShoulder = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightShoulder)
  const leftShoulder = vrmModel.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftShoulder)

  const isEku = currentModelUrl.includes('Eku')

  // Eku 模型手臂略微向内收
  baseArmRotation = isEku ? 1.12 : 1.22
  forearmRotation = -0.1
  if (rightUpperArm) { rightUpperArm.rotation.z = baseArmRotation; rightUpperArm.rotation.x = 0 }
  if (leftUpperArm) { leftUpperArm.rotation.z = -baseArmRotation; leftUpperArm.rotation.x = 0 }
  if (rightLowerArm) rightLowerArm.rotation.x = forearmRotation
  if (leftLowerArm) leftLowerArm.rotation.x = forearmRotation
  if (rightShoulder) { rightShoulder.rotation.z = 0; rightShoulder.rotation.x = 0 }
  if (leftShoulder) { leftShoulder.rotation.z = 0; leftShoulder.rotation.x = 0 }
}

let currentModelUrl = '/models/avatar.vrm'

function loadVRM(url?: string) {
  if (url) currentModelUrl = url
  const loader = new GLTFLoader()
  loader.register((parser: any) => new VRMLoaderPlugin(parser))

  isLoading.value = true
  loadError.value = false

  loader.load(
    currentModelUrl,
    (gltf) => {
      const loadedVrm = gltf.userData.vrm as VRM
      if (!loadedVrm) {
        loadError.value = true
        isLoading.value = false
        return
      }

      VRMUtils.removeUnnecessaryJoints(loadedVrm.scene)
      VRMUtils.removeUnnecessaryVertices(loadedVrm.scene)
      loadedVrm.scene.visible = false

      const box = new THREE.Box3().setFromObject(loadedVrm.scene)
      const size = box.getSize(new THREE.Vector3())
      const maxDim = Math.max(size.x, size.y, size.z)
      const scale = 1.4 / maxDim
      loadedVrm.scene.scale.setScalar(scale)

      const scaledBox = new THREE.Box3().setFromObject(loadedVrm.scene)
      const scaledCenter = scaledBox.getCenter(new THREE.Vector3())
      loadedVrm.scene.position.x = -scaledCenter.x
      loadedVrm.scene.position.z = -scaledCenter.z
      loadedVrm.scene.position.y = -scaledBox.min.y

      if (loadedVrm.lookAt && camera) {
        loadedVrm.lookAt.target = camera
      }

      fixTPose(loadedVrm)

      // 模型默认朝向（不旋转）
      loadedVrm.scene.rotation.y = 0

      scene?.add(loadedVrm.scene)
      loadedVrm.scene.visible = true
      vrm = loadedVrm

      if (renderer && scene && camera) {
        renderer.render(scene, camera)
      }

      requestAnimationFrame(() => {
        isLoading.value = false
      })

      console.log('VRM 模型加载完成')
    },
    undefined,
    (error) => {
      console.error('VRM 模型加载失败:', error)
      loadError.value = true
      isLoading.value = false
    }
  )
}

// ── 渲染循环 ──

function animate() {
  animationId = requestAnimationFrame(animate)
  const delta = clock?.getDelta() ?? 0.016
  const elapsed = clock?.getElapsedTime() ?? 0

  controls?.update()
  stateTimer += delta

  if (vrm) {
    updateMoodTransition(delta)
    updateLookAt(delta)
    updateExpressions(delta, elapsed)
    updateBodyAnimation(delta, elapsed)
    vrm.update(delta)
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
}

// ── 表情平滑过渡 ──

function updateMoodTransition(delta: number) {
  // 平滑插值到目标权重
  const speed = 3.0 // 过渡速度
  for (const key of Object.keys(moodWeights) as Mood[]) {
    moodWeights[key] += (targetMoodWeights[key] - moodWeights[key]) * Math.min(delta * speed, 1)
  }
}

// ── 视线交互 ──

function updateLookAt(delta: number) {
  if (!vrm?.lookAt || !camera) return

  // 计算目标视线位置
  const target = new THREE.Vector3()

  switch (lookAtMode) {
    case 'mouse':
      // 鼠标位置映射到 3D 空间（加大偏移幅度）
      target.set(
        mouseNDC.x * 2.0,         // 左右偏移（±2.0）
        1.05 + mouseNDC.y * 1.2,  // 上下偏移（±1.2）
        1.8
      )
      break
    case 'input':
      target.copy(inputLookAtPos)
      break
    case 'camera':
    default:
      target.copy(camera.position)
      break
  }

  // 平滑过渡视线目标
  lookAtTargetPos.lerp(target, Math.min(delta * 5, 1))

  // 更新 LookAt（通过移动 camera 的 lookAt 代理点）
  // VRM LookAt 使用的是 target 对象的 position
  if (vrm.lookAt) {
    // 创建一个辅助对象作为 LookAt 目标
    if (!(vrm.lookAt as any).__helper) {
      const helper = new THREE.Object3D()
      if (scene) scene.add(helper)
      ;(vrm.lookAt as any).__helper = helper
      vrm.lookAt.target = helper
    }
    const helper = (vrm.lookAt as any).__helper as THREE.Object3D
    helper.position.copy(lookAtTargetPos)
  }
}

// ── 表情 + 口型 + 眨眼 ──

function updateExpressions(delta: number, _elapsed: number) {
  if (!vrm?.expressionManager) return

  // ── 口型动画 ──
  if (isSpeaking) {
    mouthTimer += delta
    if (mouthTimer >= mouthInterval) {
      mouthTimer = 0
      mouthInterval = 0.08 + Math.random() * 0.12
      currentMouthShape = MOUTH_SHAPES[Math.floor(Math.random() * MOUTH_SHAPES.length)]
      mouthWeight = 0.3 + Math.random() * 0.5
    }
    for (const shape of MOUTH_SHAPES) {
      const weight = shape === currentMouthShape ? mouthWeight : 0
      vrm.expressionManager.setValue(shape as any, weight)
    }
  } else {
    for (const shape of MOUTH_SHAPES) {
      vrm.expressionManager.setValue(shape as any, 0)
    }
    mouthWeight = 0
  }

  // ── 眨眼动画 ──
  blinkTimer += delta
  if (!isBlinking && blinkTimer >= nextBlinkTime) {
    isBlinking = true
    blinkProgress = 0
    blinkTimer = 0
  }
  if (isBlinking) {
    blinkProgress += delta * 8
    if (blinkProgress < 1) {
      vrm.expressionManager.setValue(VRMExpressionPresetName.Blink, Math.sin(blinkProgress * Math.PI))
    } else {
      isBlinking = false
      vrm.expressionManager.setValue(VRMExpressionPresetName.Blink, 0)
      nextBlinkTime = 2 + Math.random() * 4
    }
  }

  // ── 情绪表情（基于 mood 权重） ──
  // 说话时降低表情权重，避免口型冲突
  const expressionScale = isSpeaking ? 0.3 : 1.0

  vrm.expressionManager.setValue('happy' as any, moodWeights.happy * expressionScale)
  vrm.expressionManager.setValue('angry' as any, moodWeights.angry * expressionScale)
  vrm.expressionManager.setValue('sad' as any, moodWeights.sad * expressionScale)
  vrm.expressionManager.setValue('relaxed' as any, moodWeights.relaxed * expressionScale)
  vrm.expressionManager.setValue('surprised' as any, moodWeights.surprised * expressionScale)

  // 思考状态时加一点 relaxed（沉思感）
  if (currentState === 'thinking') {
    vrm.expressionManager.setValue('relaxed' as any, Math.max(moodWeights.relaxed, 0.2) * expressionScale)
  }

  // 追问状态时加一点 angry（严肃感）
  if (currentState === 'probing' && moodWeights.neutral > 0.5) {
    vrm.expressionManager.setValue('angry' as any, 0.15 * expressionScale)
  }
}

// ── 骨骼动画（按状态分类） ──

function updateBodyAnimation(_delta: number, elapsed: number) {
  if (!vrm?.humanoid) return

  const head = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.Head)
  const spine = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.Spine)
  const rightUpperArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightUpperArm)
  const rightLowerArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightLowerArm)
  const leftUpperArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftUpperArm)
  const leftLowerArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.LeftLowerArm)

  switch (currentState) {
    case 'thinking':
      animateThinking(head, spine, rightUpperArm, rightLowerArm, leftUpperArm, leftLowerArm, elapsed)
      break
    case 'satisfied':
      animateSatisfied(head, spine, rightUpperArm, rightLowerArm, leftUpperArm, leftLowerArm, elapsed)
      break
    case 'probing':
      animateProbing(head, spine, rightUpperArm, rightLowerArm, leftUpperArm, leftLowerArm, elapsed)
      break
    case 'idle':
    default:
      if (isSpeaking) {
        animateSpeaking(head, spine, rightUpperArm, rightLowerArm, leftUpperArm, leftLowerArm, elapsed)
      } else {
        animateIdle(head, spine, rightUpperArm, rightLowerArm, leftUpperArm, leftLowerArm, elapsed)
      }
      break
  }
}

// ── 待机动画 ──
function animateIdle(head: any, spine: any, rUA: any, rLA: any, lUA: any, lLA: any, t: number) {
  if (head) {
    head.rotation.x = Math.sin(t * 0.6) * 0.01
    head.rotation.y = Math.sin(t * 0.4) * 0.008
    head.rotation.z = Math.sin(t * 0.5) * 0.005
  }
  if (spine) {
    spine.rotation.x = Math.sin(t * 0.8) * 0.005
    spine.rotation.z = Math.sin(t * 0.5) * 0.003
  }
  if (rUA) { rUA.rotation.z = baseArmRotation + Math.sin(t * 0.3) * 0.01; rUA.rotation.x = 0 }
  if (rLA) rLA.rotation.x = forearmRotation
  if (lUA) lUA.rotation.z = -baseArmRotation + Math.sin(t * 0.3) * 0.01
  if (lLA) lLA.rotation.x = forearmRotation
}

// ── 说话动画 ──
function animateSpeaking(head: any, spine: any, rUA: any, rLA: any, lUA: any, lLA: any, t: number) {
  if (head) {
    head.rotation.x = 0.02 + Math.sin(t * 2.5) * 0.04
    head.rotation.z = Math.sin(t * 1.2) * 0.03
    head.rotation.y = Math.sin(t * 0.8) * 0.02
  }
  if (spine) {
    spine.rotation.x = 0.02 + Math.sin(t * 1.0) * 0.01
  }
  if (rUA) { rUA.rotation.z = baseArmRotation + Math.sin(t * 1.5) * 0.1; rUA.rotation.x = Math.sin(t * 2.0) * 0.08 }
  if (rLA) rLA.rotation.x = forearmRotation - 0.2 + Math.sin(t * 2.5) * 0.15
  if (lUA) lUA.rotation.z = -baseArmRotation + Math.sin(t * 0.5) * 0.02
  if (lLA) lLA.rotation.x = forearmRotation
}

// ── 思考中：手摸下巴 ──
function animateThinking(head: any, spine: any, rUA: any, rLA: any, lUA: any, lLA: any, t: number) {
  // 头微低，微侧
  if (head) {
    head.rotation.x = 0.05 + Math.sin(t * 0.8) * 0.02
    head.rotation.z = 0.05 + Math.sin(t * 0.5) * 0.01
    head.rotation.y = Math.sin(t * 0.3) * 0.02
  }
  // 脊柱微前倾
  if (spine) {
    spine.rotation.x = 0.03 + Math.sin(t * 0.6) * 0.01
  }
  // 右手抬起摸下巴
  if (rUA) {
    rUA.rotation.z = 0.8 + Math.sin(t * 0.4) * 0.03
    rUA.rotation.x = -0.6 + Math.sin(t * 0.5) * 0.02
  }
  if (rLA) {
    rLA.rotation.x = -1.2 + Math.sin(t * 0.6) * 0.05
  }
  // 左手自然
  if (lUA) lUA.rotation.z = -baseArmRotation + Math.sin(t * 0.3) * 0.01
  if (lLA) lLA.rotation.x = forearmRotation
}

// ── 满意：点头 + 微笑 ──
function animateSatisfied(head: any, spine: any, rUA: any, rLA: any, lUA: any, lLA: any, t: number) {
  // 点头动作（较明显）
  if (head) {
    head.rotation.x = 0.05 + Math.sin(t * 3.0) * 0.08
    head.rotation.z = Math.sin(t * 1.0) * 0.02
    head.rotation.y = 0
  }
  // 脊柱放松
  if (spine) {
    spine.rotation.x = Math.sin(t * 1.0) * 0.01
  }
  // 双手自然
  if (rUA) { rUA.rotation.z = baseArmRotation + Math.sin(t * 0.5) * 0.02; rUA.rotation.x = 0 }
  if (rLA) rLA.rotation.x = forearmRotation
  if (lUA) lUA.rotation.z = -baseArmRotation + Math.sin(t * 0.5) * 0.02
  if (lLA) lLA.rotation.x = forearmRotation
}

// ── 追问：身体前倾 + 严肃 ──
function animateProbing(head: any, spine: any, rUA: any, rLA: any, lUA: any, lLA: any, t: number) {
  // 头部微前伸，严肃
  if (head) {
    head.rotation.x = 0.06 + Math.sin(t * 1.5) * 0.02
    head.rotation.z = Math.sin(t * 0.8) * 0.01
    head.rotation.y = Math.sin(t * 0.5) * 0.015
  }
  // 脊柱明显前倾
  if (spine) {
    spine.rotation.x = 0.06 + Math.sin(t * 0.8) * 0.01
  }
  // 双手交叉或自然（严肃姿态）
  if (rUA) {
    rUA.rotation.z = baseArmRotation - 0.12 + Math.sin(t * 0.4) * 0.02
    rUA.rotation.x = -0.1
  }
  if (rLA) rLA.rotation.x = -0.5
  if (lUA) {
    lUA.rotation.z = -baseArmRotation + 0.12 + Math.sin(t * 0.4) * 0.02
    lUA.rotation.x = -0.1
  }
  if (lLA) lLA.rotation.x = -0.5
}

// ── 清理 ──

function disposeThree() {
  if (animationId !== null) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  controls?.dispose()
  controls = null
  resizeObserver?.disconnect()
  resizeObserver = null
  if (vrm) {
    // 清理 lookAt helper
    if (vrm.lookAt && (vrm.lookAt as any).__helper) {
      scene?.remove((vrm.lookAt as any).__helper)
    }
    vrm.scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.geometry.dispose()
        if (Array.isArray(child.material)) {
          child.material.forEach((m) => m.dispose())
        } else {
          child.material.dispose()
        }
      }
    })
    vrm = null
  }
  renderer?.dispose()
  renderer = null
  scene = null
  camera = null
  clock = null
}

onMounted(() => {
  initThree()
  // 监听整个窗口的鼠标移动
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseleave', onMouseLeave)
})
onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseleave', onMouseLeave)
  disposeThree()
})
</script>
