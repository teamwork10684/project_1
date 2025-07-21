<template>
  <div class="document-player-panel">
    <!-- 上栏：功能按钮 -->
    <div class="toolbar">
      <a-upload :show-upload-list="false" :before-upload="handleBeforeUpload" accept=".pdf,.ppt,.pptx">
        <a-button type="primary" :disabled="!props.canUpload">上传文件</a-button>
      </a-upload>
      <a-select v-model:value="selectedFileId" style="width: 320px; margin: 0 12px;" placeholder="选择文件"
        @change="handleSelectFile" :options="fileList.map(f => ({ label: f.name, value: f.id }))"
        :dropdownRender="dropdownRender" />
      <a-divider type="vertical" />
      <button
        class="cool-speech-btn"
        @click="handleSpeechButton"
        :disabled="roomStatus === 2"
      >
        <span v-if="roomStatus === 0">开始演讲</span>
        <span v-else-if="roomStatus === 1">结束演讲</span>
        <span v-else>演讲已结束</span>
      </button>
    </div>
    <!-- 下栏：文件播放区 -->
    <div class="player-area">
      <div v-if="!selectedFileUrl">
        <div class="empty-tip">请选择要预览的文件</div>
      </div>
      <div v-show="selectedFileUrl" class="player-main" ref="playerMainRef">
        <!-- 顶部可折叠的半透明条形框 -->
        <transition name="fade">
          <div v-show="showPageBar && (isPagedType && selectedFileUrl)" class="page-bar">
            <a-button size="small" @click="prevPage" :disabled="currentPage <= 1" class="page-btn">上一页</a-button>
            <span class="page-info">第 {{ currentPage }} / {{ pageCount }} 页</span>
            <a-button size="small" @click="nextPage" :disabled="currentPage >= pageCount" class="page-btn">下一页</a-button>
            <a-button type="text" size="small" class="collapse-btn" @click="showPageBar = false">收起</a-button>
          </div>
        </transition>
        <a-button v-if="!showPageBar && (isPagedType && selectedFileUrl)" class="expand-bar-btn" type="text" size="small" @click="showPageBar = true">显示翻页栏</a-button>
        <div v-if="selectedFileType === 'pdf'" class="pdf-content" @wheel="handleWheel" @click="handleClick">
          <PdfViewer :src="selectedFileUrl" :page="currentPage" />
        </div>
        <div v-else class="empty-tip">暂不支持该文件类型预览</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { message } from 'ant-design-vue';
import { Modal } from 'ant-design-vue';
import { fileAPI } from '../api/index.js';
// 引入vue-office组件
import PdfViewer from './PdfViewer.vue';
//import '@vue-office/pptx/lib/index.css';

const props = defineProps({
  roomId: {
    type: Number,
    required: true
  },
  token: {
    type: String,
    required: true
  },
  roomStatus: {
    type: Number,
    required: false,
    default: 0
  },
  canUpload: {
    type: Boolean,
    required: false,
    default: true
  }
});

const emit = defineEmits(['start-speech', 'end-speech']);

const fileList = ref([]); // [{id, name, type, ...}]
const selectedFileId = ref(null);
const currentPage = ref(1);
const selectedFileUrl = ref('');
const selectedFileType = ref('');
const pdfPageCount = ref(1);
const showPageBar = ref(true);
// 支持pdf和pptx的统一翻页逻辑
const isPagedType = computed(() => selectedFileType.value === 'pdf');
const pageCount = computed(() => pdfPageCount.value);

// 获取PDF总页数
const fetchPdfPageCount = async (url) => {
  try {
    const pdfjsLib = await import('pdfjs-dist/legacy/build/pdf');
    const pdf = await pdfjsLib.getDocument(url).promise;
    pdfPageCount.value = pdf.numPages;
  } catch (e) {
    pdfPageCount.value = 1;
  }
};

watch([selectedFileUrl, selectedFileType], ([url, type]) => {
  if (type === 'pdf' && url) {
    fetchPdfPageCount(url);
    currentPage.value = 1;
  }
});

// 新增：emit page-change 事件
watch([currentPage, selectedFileId], ([page, fileId]) => {
  emit('page-change', { fileId, page });
});

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--;
};
const nextPage = () => {
  if (currentPage.value < pageCount.value) currentPage.value++;
};

const fetchFileList = async () => {
  try {
    const res = await fileAPI.getFileList(props.roomId, props.token);
    if (res.data && Array.isArray(res.data.files)) {
      fileList.value = res.data.files.map(f => ({
        id: f.id,
        name: f.filename,
        type: (f.file_extension || '').toLowerCase(), // 用扩展名判断类型
        ...f
      }));
    }
  } catch (e) {
    message.error('获取文件列表失败');
  }
};
onMounted(fetchFileList);

const handleBeforeUpload = async (file) => {
  if (!props.canUpload) {
    message.error('演讲已结束，无法上传文件');
    return false;
  }
  const ext = file.name.split('.').pop().toLowerCase();
  if (!['pdf', 'ppt', 'pptx'].includes(ext)) {
    message.error('仅支持PDF、PPT、PPTX格式');
    return false;
  }
  const formData = new FormData();
  formData.append('file', file);
  formData.append('room_id', props.roomId);
  formData.append('token', props.token);
  try {
    await fileAPI.uploadFile(formData);
    message.success('上传成功');
    fetchFileList();
  } catch (e) {
    message.error(e?.response?.data?.message || '上传失败');
  }
  return false; // 阻止自动上传
};

const handleSelectFile = async (id) => {
  currentPage.value = 1;
  const file = fileList.value.find(f => f.id === id);
  if (!file) return;
  if (!['pdf'].includes(file.type)) {
    message.error('仅支持PDF文件预览');
    selectedFileUrl.value = '';
    selectedFileType.value = '';
    return;
  }
  try {
    const res = await fileAPI.getFileUrl(props.roomId, id);
    selectedFileUrl.value = res.data.url;
    selectedFileType.value = file.type;
  } catch (e) {
    message.error('获取文件URL失败');
    selectedFileUrl.value = '';
    selectedFileType.value = '';
  }
};

const handleDeleteFileById = async (id) => {
  try {
    await fileAPI.deleteFile(id, props.token);
    message.success('删除成功');
    fetchFileList();
  } catch (e) {
    message.error(e?.response?.data?.message || '删除失败');
  }
};

const handleSpeechButton = () => {
  if (props.roomStatus === 0) {
    emit('start-speech');
  } else if (props.roomStatus === 1) {
    Modal.confirm({
      title: '确认结束演讲',
      content: '结束后将无法再次开始演讲，确定要结束吗？',
      okText: '确定',
      cancelText: '取消',
      onOk() {
        emit('end-speech');
      }
    });
  }
};

// 自定义下拉渲染，显示删除按钮
import { h } from 'vue';
const dropdownRender = (originNode) => {
  return h('div', {}, [
    h('div', {},
      fileList.value.map(file =>
        h('div', {
          style: {
            display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', padding: '4px 12px', cursor: 'pointer',
            background: file.id === selectedFileId.value ? '#f5f5f5' : 'white',
          },
          onClick: () => { selectedFileId.value = file.id; handleSelectFile(file.id); }
        }, [
          h('span', { class: 'file-name-ellipsis', style: { maxWidth: '180px', flex: '1 1 auto', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'inline-block' } }, file.name),
          h('a-button', {
            type: 'link', size: 'small', style: 'color: #ff4d4f; margin-left: 8px;',
            onClick: (e) => { e.stopPropagation(); handleDeleteFileById(file.id); }
          }, '删除')
        ])
      )
    )
  ]);
};

// 鼠标滚轮/点击/键盘翻页
let playerMainRef = ref(null);
const handleWheel = (e) => {
  console.log('wheel event', e.deltaY);
  if (!isPagedType.value || !selectedFileUrl.value) return;
  if (e.deltaY > 0) nextPage();
  else if (e.deltaY < 0) prevPage();
};
const handleClick = (e) => {
  console.log('click event', e.clientX, e.clientY);
  if (!isPagedType.value || !selectedFileUrl.value) return;
  // 左半区上一页，右半区下一页
  const rect = e.currentTarget.getBoundingClientRect();
  const x = e.clientX - rect.left;
  if (x < rect.width / 2) prevPage();
  else nextPage();
};
const handleKeydown = (e) => {
  if (!isPagedType.value || !selectedFileUrl.value) return;
  if (e.key === 'ArrowUp') prevPage();
  else if (e.key === 'ArrowDown') nextPage();
};
onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.document-player-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  overflow: hidden;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  min-height: 56px;
  gap: 8px;
  position: relative;
}

/* 新增：按钮靠右 */
.toolbar {
  justify-content: flex-start;
}

.cool-speech-btn {
  margin-left: auto;
}

.player-area {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  background: #f5f7fa;
  width: 100%;
  height: 100%;
  overflow: auto;
}

.player-controls {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.player-content {
  width: 100%;
  height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.05);
  overflow: hidden;
}

.empty-tip {
  color: #999;
  font-style: italic;
  text-align: center;
}

.cool-speech-btn {
  position: relative;
  width: 140px;
  min-width: 140px;
  max-width: 140px;
  height: 44px;
  font-size: 15px;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(270deg, #ff512f, #dd2476, #1fa2ff, #24ff72, #ff512f);
  background-size: 400% 400%;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s;
  outline: none;
  z-index: 1;
  animation: gradient-move 3s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cool-speech-btn:hover {
  transform: scale(1.07) rotate(-1deg);
}

.cool-speech-btn.speaking {
  animation: none;
  background: linear-gradient(90deg, #333 0%, #666 100%);
  opacity: 1;
  cursor: pointer;
}

.cool-speech-btn:disabled {
  animation: none;
  background: linear-gradient(90deg, #333 0%, #666 100%);
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes gradient-move {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.file-name-ellipsis {
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
  flex: 1 1 auto;
}

.pdf-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 12px;
}

.pdf-content {
  flex: 1 1 0;
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  background: #fff;
}

.page-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(30, 30, 30, 0.55);
  color: #fff;
  padding: 8px 0;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  gap: 12px;
  transition: opacity 0.2s;
}
.page-info {
  font-size: 15px;
  font-weight: 500;
  margin: 0 8px;
  color: #fff;
}
.page-btn {
  min-width: 60px;
}
.collapse-btn {
  position: absolute;
  right: 16px;
  top: 6px;
  color: #fff;
  opacity: 0.7;
}
.expand-bar-btn {
  position: absolute;
  top: 8px;
  right: 16px;
  z-index: 11;
  background: rgba(30,30,30,0.3);
  color: #fff;
  border-radius: 6px;
  font-size: 13px;
  padding: 2px 10px;
  opacity: 0.7;
}
.player-main {
  position: relative;
  flex: 1 1 0;
  width: 100%;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>