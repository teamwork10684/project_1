<template>
  <div class="pdf-viewer" ref="containerRef">
    <canvas ref="canvasRef"></canvas>
    <div v-if="loading" class="pdf-loading">加载中...</div>
    <div v-if="error" class="pdf-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf'
import 'pdfjs-dist/legacy/web/pdf_viewer.css'

const props = defineProps({
  src: { type: String, required: true },
  page: { type: Number, default: 1 }
})

const canvasRef = ref(null)
const containerRef = ref(null)
const loading = ref(false)
const error = ref('')
let pdfDoc = null
let lastUrl = ''
let lastPage = 1
let resizeObserver = null

const renderPdf = async (url, pageNum) => {
  loading.value = true
  error.value = ''
  try {
    await nextTick();
    if (!pdfDoc || pdfDoc._url !== url) {
      pdfDoc = await pdfjsLib.getDocument(url).promise
      pdfDoc._url = url
    }
    const page = await pdfDoc.getPage(pageNum)
    const container = containerRef.value
    const containerWidth = container ? container.clientWidth : 800
    const containerHeight = container ? container.clientHeight : 600
    const viewport0 = page.getViewport({ scale: 1 })
    // 取宽高比的最小值，保证不变形且最大填充
    const scale = Math.min(
      containerWidth / viewport0.width,
      containerHeight / viewport0.height
    )
    const viewport = page.getViewport({ scale })
    const canvas = canvasRef.value
    const context = canvas.getContext('2d')
    canvas.width = viewport.width
    canvas.height = viewport.height
    // 让canvas在容器内居中
    canvas.style.display = 'block'
    canvas.style.margin = '0 auto'
    await page.render({ canvasContext: context, viewport }).promise
    lastUrl = url
    lastPage = pageNum
  } catch (e) {
    error.value = 'PDF 加载失败'
  } finally {
    loading.value = false
  }
}

const rerender = () => {
  if (props.src) renderPdf(props.src, props.page)
}

watch(() => [props.src, props.page], ([newSrc, newPage]) => {
  rerender()
})

onMounted(() => {
  rerender()
  // 监听容器尺寸变化，自适应重渲染
  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      rerender()
    })
    resizeObserver.observe(containerRef.value)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
  }
})
</script>

<style scoped>
.pdf-viewer {
  width: 100%;
  height: 100%;
  position: relative;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
canvas {
  max-width: 100%;
  max-height: 100%;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  display: block;
}
.pdf-loading, .pdf-error {
  position: absolute;
  left: 0; right: 0; top: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
  font-size: 16px;
  background: rgba(255,255,255,0.7);
}
</style> 