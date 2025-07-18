<template>
  <div ref="revealContainer" class="ppt-viewer" />
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import Reveal from 'reveal.js'
import Markdown from 'reveal.js/plugin/markdown/markdown.esm.js'
import 'reveal.js/dist/reveal.css'
import 'reveal.js/dist/theme/white.css'

const props = defineProps({
  src: { type: String, default: '' }, // 直接传内容
  file: { type: String, default: '' }, // 静态文件链接
  page: { type: Number, default: 1 }
})

const revealContainer = ref(null)
let revealInstance = null
let slideCount = 1
let lastContent = ''

const fetchFileContent = async (fileUrl) => {
  if (!fileUrl) return ''
  if (fileUrl.endsWith('.md')) {
    const res = await fetch(fileUrl)
    if (!res.ok) throw new Error('无法加载Markdown文件')
    const md = await res.text()
    // 用reveal.js markdown插件渲染
    return `<section data-markdown><textarea data-template>${md}</textarea></section>`
  } else if (fileUrl.endsWith('.html')) {
    const res = await fetch(fileUrl)
    if (!res.ok) throw new Error('无法加载HTML文件')
    return await res.text()
  } else if (fileUrl.endsWith('.pptx')) {
    return `<section><h2>暂不支持前端直接解析PPTX，请先转为markdown或html</h2></section>`
  } else {
    return `<section><h2>不支持的文件类型</h2></section>`
  }
}

const getContent = async () => {
  if (props.file) {
    return await fetchFileContent(props.file)
  } else {
    return props.src
  }
}

const initReveal = async () => {
  if (!revealContainer.value) return
  // 清空容器
  revealContainer.value.innerHTML = ''
  // 获取内容
  const content = await getContent()
  lastContent = content
  // 创建slides容器
  const slides = document.createElement('div')
  slides.className = 'reveal'
  slides.innerHTML = `<div class='slides'>${content}</div>`
  revealContainer.value.appendChild(slides)
  // 初始化reveal
  revealInstance = new Reveal(slides, { embedded: true, plugins: [Markdown] })
  await revealInstance.initialize()
  slideCount = revealInstance.getTotalSlides()
  // 跳转到指定页
  revealInstance.slide(props.page - 1)
}

watch(() => [props.src, props.file], async ([newSrc, newFile]) => {
  await initReveal()
})
watch(() => props.page, (val) => {
  if (revealInstance) revealInstance.slide(val - 1)
})

onMounted(() => {
  initReveal()
})
onBeforeUnmount(() => {
  if (revealInstance) {
    revealInstance.destroy()
    revealInstance = null
  }
})
</script>

<style scoped>
.ppt-viewer {
  width: 100%;
  height: 100%;
  background: #fff;
  overflow: hidden;
}
.reveal {
  width: 100%;
  height: 100%;
}
.slides {
  width: 100%;
  height: 100%;
}
</style> 