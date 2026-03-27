<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Check, Connection, CopyDocument, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import { useClipboard } from '@vueuse/core'

const API_BASE = 'http://localhost:8000'
const MODEL_CONFIG_STORAGE_KEY = 'prd-pilot-model-config-v1'
const FALLBACK_MODEL_OPTIONS = {
  providers: [
    { id: 'deepseek', label: 'DeepSeek', base_url: 'https://api.deepseek.com/v1', models: [{ id: 'deepseek-chat', label: 'deepseek-chat' }, { id: 'deepseek-reasoner', label: 'deepseek-reasoner' }] },
    { id: 'openai', label: 'OpenAI', base_url: 'https://api.openai.com/v1', models: [{ id: 'gpt-4.1-mini', label: 'gpt-4.1-mini' }, { id: 'gpt-4.1', label: 'gpt-4.1' }, { id: 'gpt-4o-mini', label: 'gpt-4o-mini' }, { id: 'gpt-4o', label: 'gpt-4o' }, { id: 'gpt-5-mini', label: 'gpt-5-mini' }, { id: 'gpt-5', label: 'gpt-5' }] },
    { id: 'openrouter', label: 'OpenRouter', base_url: 'https://openrouter.ai/api/v1', models: [{ id: 'openai/gpt-4.1-mini', label: 'openai/gpt-4.1-mini' }, { id: 'deepseek/deepseek-chat-v3-0324', label: 'deepseek/deepseek-chat-v3-0324' }, { id: 'anthropic/claude-3.7-sonnet', label: 'anthropic/claude-3.7-sonnet' }, { id: 'google/gemini-2.5-flash', label: 'google/gemini-2.5-flash' }] },
    { id: 'zhipu', label: 'Zhipu / GLM', base_url: 'https://open.bigmodel.cn/api/paas/v4/', models: [{ id: 'glm-4.5-air', label: 'glm-4.5-air' }, { id: 'glm-4.5', label: 'glm-4.5' }, { id: 'glm-4-plus', label: 'glm-4-plus' }] },
    { id: 'siliconflow', label: 'SiliconFlow', base_url: 'https://api.siliconflow.cn/v1', models: [{ id: 'Qwen/Qwen3-32B', label: 'Qwen/Qwen3-32B' }, { id: 'deepseek-ai/DeepSeek-V3', label: 'deepseek-ai/DeepSeek-V3' }, { id: 'THUDM/GLM-4-9B-Chat', label: 'THUDM/GLM-4-9B-Chat' }] },
    { id: 'moonshot', label: 'Moonshot', base_url: 'https://api.moonshot.cn/v1', models: [{ id: 'moonshot-v1-8k', label: 'moonshot-v1-8k' }, { id: 'moonshot-v1-32k', label: 'moonshot-v1-32k' }, { id: 'moonshot-v1-128k', label: 'moonshot-v1-128k' }] },
    { id: 'groq', label: 'Groq', base_url: 'https://api.groq.com/openai/v1', models: [{ id: 'llama-3.3-70b-versatile', label: 'llama-3.3-70b-versatile' }, { id: 'llama-3.1-8b-instant', label: 'llama-3.1-8b-instant' }, { id: 'openai/gpt-oss-20b', label: 'openai/gpt-oss-20b' }] },
    { id: 'dashscope', label: 'DashScope / Qwen', base_url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', models: [{ id: 'qwen-turbo', label: 'qwen-turbo' }, { id: 'qwen-plus', label: 'qwen-plus' }, { id: 'qwen-max', label: 'qwen-max' }] },
    { id: 'ollama', label: 'Ollama (Local)', base_url: 'http://localhost:11434/v1', models: [{ id: 'qwen2.5:7b', label: 'qwen2.5:7b' }, { id: 'llama3.1:8b', label: 'llama3.1:8b' }, { id: 'deepseek-r1:8b', label: 'deepseek-r1:8b' }] },
    { id: 'custom', label: 'Custom OpenAI Compatible', base_url: '', models: [] }
  ],
  default_config: { provider: 'deepseek', model: 'deepseek-chat', base_url: 'https://api.deepseek.com/v1', max_tokens: 0, has_env_api_key: false }
}
const md = new MarkdownIt({ html: false, linkify: true, typographer: true })
const inputMode = ref('quick')
const outputTab = ref('prd')
const demoView = ref('preview')
const loadingAction = ref('')
const modelConfigVisible = ref(false)
const modelOptions = ref(FALLBACK_MODEL_OPTIONS.providers)
const hasServerDefaultKey = ref(false)
const modelConfigStatus = ref('')
const testingModel = ref(false)
const modelDefaults = ref(FALLBACK_MODEL_OPTIONS.default_config)

const modelConfig = reactive({ provider: 'deepseek', model: 'deepseek-chat', api_key: '', base_url: 'https://api.deepseek.com/v1', max_tokens: null })
const quickForm = reactive({ idea: '', notes: '', stylePreference: '' })
const structuredForm = reactive({
  product_name: '', product_type: '', problem_statement: '', target_users: '', user_pain_points: '',
  key_scenarios: '', core_features: '', primary_pages_hint: '', page_count_preference: '',
  demo_focus: '', feature_preferences: '', constraints: '', tech_stack: '', delivery_notes: ''
})
const specEditor = reactive({
  product_name: '', product_type: '', target_users: '', user_pain_points: '', core_scenarios: '',
  key_features: '', primary_pages: '', user_flow: '', style_preference: '', constraints: '', success_criteria: ''
})
const iterationForm = reactive({ change_type: 'clarify_flow', target_module: 'demo', affected_pages: [], instruction: '' })
const result = reactive({ prd: '', demoHtml: '', prototypeOutline: '', consistency: null, changeSummary: '', changedSections: [], affectedPages: [] })

const styleOptions = [
  { label: '不限定', value: '' },
  { label: '原生 HTML 原型', value: '原生 HTML 原型' },
  { label: 'Vue 风格', value: 'Vue 风格' },
  { label: 'React 风格', value: 'React 风格' },
  { label: '移动端 H5', value: '移动端 H5' },
  { label: '后台管理台', value: '后台管理台' }
]
const changeTypeOptions = [
  { label: '梳理关键流程', value: 'clarify_flow' },
  { label: '调整目标用户', value: 'modify_user' },
  { label: '新增一个页面', value: 'add_page' },
  { label: '删除某个功能', value: 'remove_feature' },
  { label: '调整首页层级', value: 'adjust_layout' },
  { label: '切换原型风格', value: 'change_style' },
  { label: '强化数据展示', value: 'improve_data_density' },
  { label: '精简 PRD 篇幅', value: 'simplify_prd' }
]
const targetModuleOptions = [
  { label: 'PRD', value: 'prd' },
  { label: 'Demo', value: 'demo' },
  { label: '原型说明', value: 'prototype_outline' }
]
const { copy, copied } = useClipboard()

const selectedProvider = computed(() => modelOptions.value.find((item) => item.id === modelConfig.provider) || FALLBACK_MODEL_OPTIONS.providers[0])
const currentModelChoices = computed(() => selectedProvider.value?.models || [])
const providerRequiresApiKey = computed(() => modelConfig.provider !== 'ollama')
const maxTokensInput = computed({
  get: () => (modelConfig.max_tokens ? String(modelConfig.max_tokens) : ''),
  set: (value) => {
    const text = String(value ?? '').trim()
    const parsed = Number(text)
    modelConfig.max_tokens = text && Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : null
  }
})
const modelStatusText = computed(() => {
  if (modelConfigStatus.value) return modelConfigStatus.value
  const messages = []
  if (modelConfig.provider === 'ollama') messages.push('本地 Ollama 模式不需要真实 API Key。')
  else if (hasServerDefaultKey.value && !modelConfig.api_key.trim()) messages.push('后端已配置默认 Key，这里可以留空。')
  if (!messages.length) messages.push('配置只保存在当前浏览器。')
  return messages.join(' ')
})
const modelSummary = computed(() => `${selectedProvider.value?.label || '未选择平台'} / ${modelConfig.model || '未填写模型'}`)

function splitLines(value) { return value.split(/\n|,|，|;|；|、/).map((item) => item.trim()).filter(Boolean) }
function joinLines(values) { return Array.isArray(values) ? values.join('\n') : '' }
function readStoredModelConfig() {
  const raw = localStorage.getItem(MODEL_CONFIG_STORAGE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch (error) {
    localStorage.removeItem(MODEL_CONFIG_STORAGE_KEY)
    return null
  }
}
function getSanitizedModelConfig() {
  return {
    provider: modelConfig.provider,
    model: modelConfig.model.trim(),
    api_key: modelConfig.api_key.trim(),
    base_url: modelConfig.base_url.trim(),
    max_tokens: Number(modelConfig.max_tokens) > 0 ? Number(modelConfig.max_tokens) : 0
  }
}
function applyModelConfig(config = {}) {
  modelConfig.provider = config.provider || FALLBACK_MODEL_OPTIONS.default_config.provider
  modelConfig.model = config.model || FALLBACK_MODEL_OPTIONS.default_config.model
  modelConfig.api_key = config.api_key || ''
  modelConfig.base_url = config.base_url || FALLBACK_MODEL_OPTIONS.default_config.base_url
  const maxTokens = Number(config.max_tokens ?? FALLBACK_MODEL_OPTIONS.default_config.max_tokens)
  modelConfig.max_tokens = maxTokens > 0 ? maxTokens : null
}
function syncProviderDefaults(provider, keepModel = false) {
  const preset = modelOptions.value.find((item) => item.id === provider)
  if (!preset) return
  modelConfig.base_url = preset.base_url || ''
  const hasCurrentModel = preset.models?.some((item) => item.id === modelConfig.model.trim())
  if (!keepModel || !modelConfig.model.trim() || (preset.models?.length && !hasCurrentModel)) {
    modelConfig.model = preset.models?.[0]?.id || ''
  }
}
function persistModelConfig() {
  localStorage.setItem(MODEL_CONFIG_STORAGE_KEY, JSON.stringify(getSanitizedModelConfig()))
}
function validateModelConfig() {
  const config = getSanitizedModelConfig()
  if (providerRequiresApiKey.value && !config.api_key && !hasServerDefaultKey.value) {
    ElMessage.warning('请先填写 API Key，或在后端配置默认 Key。')
    return false
  }
  if (!config.model) {
    ElMessage.warning('请先选择或填写模型名称。')
    return false
  }
  if (!config.base_url) {
    ElMessage.warning('请先填写 Base URL。')
    return false
  }
  return true
}
function resetModelConfig() {
  applyModelConfig(modelDefaults.value || FALLBACK_MODEL_OPTIONS.default_config)
  modelConfigStatus.value = ''
  persistModelConfig()
  ElMessage.success('模型配置已恢复为默认值。')
}
function resetSpecEditor() {
  Object.assign(specEditor, {
    product_name: '', product_type: '', target_users: '', user_pain_points: '', core_scenarios: '',
    key_features: '', primary_pages: '', user_flow: '', style_preference: '', constraints: '', success_criteria: ''
  })
}
function applyRequirementSpec(spec) {
  specEditor.product_name = spec.product_name || ''
  specEditor.product_type = spec.product_type || ''
  specEditor.target_users = joinLines(spec.target_users)
  specEditor.user_pain_points = joinLines(spec.user_pain_points)
  specEditor.core_scenarios = joinLines(spec.core_scenarios)
  specEditor.key_features = joinLines(spec.key_features)
  specEditor.primary_pages = joinLines(spec.primary_pages)
  specEditor.user_flow = joinLines(spec.user_flow)
  specEditor.style_preference = spec.style_preference || ''
  specEditor.constraints = joinLines(spec.constraints)
  specEditor.success_criteria = joinLines(spec.success_criteria)
}

const briefPayload = computed(() => inputMode.value === 'quick' ? {
  product_name: '', product_type: '', elevator_pitch: '', problem_statement: quickForm.idea.trim(), target_users: '', user_pain_points: '',
  key_scenarios: '', core_features: '', primary_pages_hint: '', page_count_preference: '', demo_focus: '', feature_preferences: '',
  success_metrics: '', constraints: '', tech_stack: quickForm.stylePreference, delivery_notes: quickForm.notes.trim()
} : {
  product_name: structuredForm.product_name.trim(), product_type: structuredForm.product_type.trim(), elevator_pitch: '',
  problem_statement: structuredForm.problem_statement.trim(), target_users: structuredForm.target_users.trim(),
  user_pain_points: structuredForm.user_pain_points.trim(), key_scenarios: structuredForm.key_scenarios.trim(),
  core_features: structuredForm.core_features.trim(), primary_pages_hint: structuredForm.primary_pages_hint.trim(),
  page_count_preference: structuredForm.page_count_preference.trim(), demo_focus: structuredForm.demo_focus.trim(),
  feature_preferences: structuredForm.feature_preferences.trim(), success_metrics: '', constraints: structuredForm.constraints.trim(),
  tech_stack: structuredForm.tech_stack, delivery_notes: structuredForm.delivery_notes.trim()
})
const requirementSpec = computed(() => ({
  product_name: specEditor.product_name.trim(), product_type: specEditor.product_type.trim(), target_users: splitLines(specEditor.target_users),
  user_pain_points: splitLines(specEditor.user_pain_points), core_scenarios: splitLines(specEditor.core_scenarios),
  key_features: splitLines(specEditor.key_features), primary_pages: splitLines(specEditor.primary_pages), user_flow: splitLines(specEditor.user_flow),
  style_preference: specEditor.style_preference, constraints: splitLines(specEditor.constraints), success_criteria: splitLines(specEditor.success_criteria)
}))
const hasRequirementSpec = computed(() => Boolean(requirementSpec.value.product_name || requirementSpec.value.key_features.length || requirementSpec.value.primary_pages.length))
const pageOptions = computed(() => splitLines(specEditor.primary_pages))
const renderedPrd = computed(() => result.prd ? md.render(result.prd) : '')
const renderedOutline = computed(() => result.prototypeOutline ? md.render(result.prototypeOutline) : '')
const currentArtifact = computed(() => outputTab.value === 'prd' ? result.prd : outputTab.value === 'demo' ? result.demoHtml : outputTab.value === 'outline' ? result.prototypeOutline : formatConsistency())

function validateInput() {
  if (inputMode.value === 'quick' && !quickForm.idea.trim()) { ElMessage.warning('请先输入需求描述。'); return false }
  if (inputMode.value === 'structured' && !Object.values(structuredForm).some((v) => String(v).trim())) { ElMessage.warning('结构化模式下请至少填写一个关键字段。'); return false }
  return true
}
function formatConsistency() {
  if (!result.consistency) return ''
  return [`一致性等级：${result.consistency.overall_level}`, `一致性评分：${result.consistency.score}`, '', ...result.consistency.checks.map((item) => `- ${item.label} [${item.status}] ${item.summary}`)].join('\n')
}
async function callApi(path, payload) {
  const response = await fetch(`${API_BASE}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
  const data = await response.json()
  if (!response.ok || data.success === false) throw new Error(data.detail || data.message || '请求失败')
  return data.data
}
async function loadModelOptions() {
  try {
    const response = await fetch(`${API_BASE}/api/model-options`)
    const data = await response.json()
    if (response.ok && data.success) {
      modelOptions.value = data.data.providers || FALLBACK_MODEL_OPTIONS.providers
      modelDefaults.value = data.data.default_config || FALLBACK_MODEL_OPTIONS.default_config
      hasServerDefaultKey.value = Boolean(data.data.default_config?.has_env_api_key)
      const storedConfig = readStoredModelConfig()
      if (storedConfig) {
        applyModelConfig(storedConfig)
      } else {
        applyModelConfig(modelDefaults.value)
      }
      if (!modelOptions.value.some((item) => item.id === modelConfig.provider)) applyModelConfig(modelDefaults.value)
      syncProviderDefaults(modelConfig.provider, true)
      persistModelConfig()
    }
  } catch (error) {
    const storedConfig = readStoredModelConfig()
    if (storedConfig) applyModelConfig(storedConfig)
    syncProviderDefaults(modelConfig.provider, true)
  }
}
async function testModelConnection() {
  if (!validateModelConfig()) return
  testingModel.value = true
  try {
    const data = await callApi('/api/test-model-config', { model_config: getSanitizedModelConfig() })
    modelConfigStatus.value = `连接成功：${data.provider} / ${data.model}`
    ElMessage.success('模型连接可用。')
  } catch (error) {
    modelConfigStatus.value = `连接失败：${error.message}`
    ElMessage.error(error.message)
  } finally {
    testingModel.value = false
  }
}
async function ensureRequirementSpec() {
  if (hasRequirementSpec.value) return requirementSpec.value
  const data = await callApi('/api/structure-requirement', { brief: briefPayload.value, model_config: getSanitizedModelConfig() })
  applyRequirementSpec(data.requirement_spec)
  return requirementSpec.value
}
async function structureRequirement() {
  if (!validateInput()) return
  if (!validateModelConfig()) return
  loadingAction.value = 'structure'
  try {
    const data = await callApi('/api/structure-requirement', { brief: briefPayload.value, model_config: getSanitizedModelConfig() })
    applyRequirementSpec(data.requirement_spec)
    ElMessage.success('需求摘要已生成。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
async function generatePrd() {
  if (!validateInput()) return
  if (!validateModelConfig()) return
  loadingAction.value = 'prd'
  try {
    const spec = await ensureRequirementSpec()
    const data = await callApi('/api/generate-prd', { brief: briefPayload.value, requirement_spec: spec, model_config: getSanitizedModelConfig() })
    applyRequirementSpec(data.requirement_spec)
    result.prd = data.prd
    outputTab.value = 'prd'
    ElMessage.success('PRD 已生成。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
async function generateDemo() {
  if (!validateInput()) return
  if (!validateModelConfig()) return
  loadingAction.value = 'demo'
  try {
    const spec = await ensureRequirementSpec()
    const data = await callApi('/api/generate-demo', { brief: briefPayload.value, requirement_spec: spec, prd_content: result.prd || undefined, model_config: getSanitizedModelConfig() })
    applyRequirementSpec(data.requirement_spec)
    result.demoHtml = data.demo_html
    result.prototypeOutline = data.prototype_outline
    demoView.value = 'preview'
    outputTab.value = 'demo'
    ElMessage.success('Demo 与原型说明已生成。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
async function runConsistencyCheck() {
  if (!hasRequirementSpec.value) { ElMessage.warning('请先生成需求摘要。'); return }
  if (!result.prd && !result.demoHtml) { ElMessage.warning('请先生成 PRD 或 Demo。'); return }
  loadingAction.value = 'consistency'
  try {
    result.consistency = await callApi('/api/check-consistency', {
      requirement_spec: requirementSpec.value,
      prd: result.prd,
      demo_html: result.demoHtml,
      prototype_outline: result.prototypeOutline
    })
    outputTab.value = 'consistency'
    ElMessage.success('一致性检查完成。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
function applyChangeMeta(data) {
  result.changeSummary = data.change_summary || ''
  result.changedSections = data.changed_sections || []
  result.affectedPages = data.affected_pages || []
}
function applyRepairSuggestion(suggestion) {
  iterationForm.instruction = suggestion
  iterationForm.change_type = suggestion.includes('页面') ? 'add_page' : suggestion.includes('风格') ? 'change_style' : suggestion.includes('功能') ? 'remove_feature' : suggestion.includes('数据') ? 'improve_data_density' : 'clarify_flow'
  iterationForm.target_module = suggestion.includes('PRD') ? 'prd' : 'demo'
  ElMessage.success('修复建议已带入修改区。')
}
async function iteratePrd() {
  if (!result.prd) { ElMessage.warning('请先生成 PRD。'); return }
  if (!iterationForm.instruction.trim()) { ElMessage.warning('请先填写本次修改说明。'); return }
  if (!validateModelConfig()) return
  loadingAction.value = 'iterate-prd'
  try {
    const data = await callApi('/api/iterate-prd', {
      model_config: getSanitizedModelConfig(),
      brief: briefPayload.value, requirement_spec: requirementSpec.value, change_type: iterationForm.change_type,
      target_module: iterationForm.target_module, affected_pages: iterationForm.affected_pages, instruction: iterationForm.instruction,
      current_prd: result.prd, current_demo_html: result.demoHtml, current_prototype_outline: result.prototypeOutline
    })
    applyRequirementSpec(data.requirement_spec)
    result.prd = data.prd
    applyChangeMeta(data)
    outputTab.value = 'prd'
    ElMessage.success('PRD 已更新。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
async function iterateDemo() {
  if (!result.demoHtml) { ElMessage.warning('请先生成 Demo。'); return }
  if (!iterationForm.instruction.trim()) { ElMessage.warning('请先填写本次修改说明。'); return }
  if (!validateModelConfig()) return
  loadingAction.value = 'iterate-demo'
  try {
    const data = await callApi('/api/iterate-demo', {
      model_config: getSanitizedModelConfig(),
      brief: briefPayload.value, requirement_spec: requirementSpec.value, change_type: iterationForm.change_type,
      target_module: iterationForm.target_module, affected_pages: iterationForm.affected_pages, instruction: iterationForm.instruction,
      current_prd: result.prd, current_demo_html: result.demoHtml, current_prototype_outline: result.prototypeOutline
    })
    applyRequirementSpec(data.requirement_spec)
    result.demoHtml = data.demo_html
    result.prototypeOutline = data.prototype_outline
    applyChangeMeta(data)
    demoView.value = 'preview'
    outputTab.value = 'demo'
    ElMessage.success('Demo 已更新。')
  } catch (error) { ElMessage.error(error.message) } finally { loadingAction.value = '' }
}
async function copyCurrentArtifact() { if (!currentArtifact.value) return; await copy(currentArtifact.value); ElMessage.success('已复制当前内容。') }
function downloadDemo() {
  if (!result.demoHtml) { ElMessage.warning('请先生成 Demo。'); return }
  const blob = new Blob([result.demoHtml], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'prd-pilot-demo.html'
  link.click()
  URL.revokeObjectURL(url)
}
function resetAll() {
  Object.assign(quickForm, { idea: '', notes: '', stylePreference: '' })
  Object.assign(structuredForm, {
    product_name: '', product_type: '', problem_statement: '', target_users: '', user_pain_points: '', key_scenarios: '', core_features: '',
    primary_pages_hint: '', page_count_preference: '', demo_focus: '', feature_preferences: '', constraints: '', tech_stack: '', delivery_notes: ''
  })
  resetSpecEditor()
  Object.assign(iterationForm, { change_type: 'clarify_flow', target_module: 'demo', affected_pages: [], instruction: '' })
  Object.assign(result, { prd: '', demoHtml: '', prototypeOutline: '', consistency: null, changeSummary: '', changedSections: [], affectedPages: [] })
  outputTab.value = 'prd'
  demoView.value = 'preview'
  ElMessage.success('已清空当前工作区。')
}

watch(() => modelConfig.provider, (provider) => {
  syncProviderDefaults(provider, true)
  modelConfigStatus.value = ''
})
watch(() => [modelConfig.provider, modelConfig.model, modelConfig.api_key, modelConfig.base_url, modelConfig.max_tokens], () => {
  persistModelConfig()
}, { deep: false })
onMounted(() => {
  loadModelOptions()
})
</script>

<template>
  <div class="page-shell">
    <header class="hero">
      <div class="hero-top">
        <div class="hero-copy-block">
          <p class="eyebrow">AI PRD & Demo Workspace</p>
          <h1>PRD Pilot</h1>
          <p class="hero-copy">面向产品经理的 AI PRD 与 Demo 快速生成工作台。把一个模糊想法，整理成可评审的 PRD、可演示的 Demo，以及可继续迭代的产品方案。</p>
        </div>
        <div class="hero-side">
          <div class="config-pill">
            <span class="pill-label">当前模型</span>
            <strong>{{ modelSummary }}</strong>
            <span class="pill-meta">{{ modelStatusText }}</span>
          </div>
          <el-button type="primary" class="config-trigger" @click="modelConfigVisible = true">配置模型</el-button>
        </div>
      </div>
    </header>

    <main class="grid">
      <div class="stack">
        <section class="card input-card">
          <div class="section-head">
            <div><h2>需求输入</h2><p>快速模式负责进入流程，结构化模式负责增强输入质量。</p></div>
            <el-radio-group v-model="inputMode" size="small">
              <el-radio-button value="quick">快速模式</el-radio-button>
              <el-radio-button value="structured">结构化模式</el-radio-button>
            </el-radio-group>
          </div>
          <div v-if="inputMode === 'quick'" class="panel-body">
            <el-form label-position="top" class="form-grid">
              <el-form-item label="需求描述"><el-input v-model="quickForm.idea" type="textarea" :rows="9" resize="none" placeholder="例如：做一个帮助学生产品经理快速整理需求、生成 PRD 和可演示 Demo 的 Web 工具。" /></el-form-item>
              <el-form-item label="补充要求"><el-input v-model="quickForm.notes" type="textarea" :rows="4" resize="none" placeholder="例如：更偏后台工作台风格，评审时要能看到状态变化。" /></el-form-item>
              <el-form-item label="原型风格"><el-select v-model="quickForm.stylePreference" class="full"><el-option v-for="option in styleOptions" :key="option.label" :label="option.label" :value="option.value" /></el-select></el-form-item>
            </el-form>
          </div>
          <div v-else class="panel-body">
            <el-form label-position="top" class="form-grid">
              <div class="cols"><el-form-item label="产品名称"><el-input v-model="structuredForm.product_name" /></el-form-item><el-form-item label="产品类型"><el-input v-model="structuredForm.product_type" placeholder="例如：Web 工具 / H5 / 后台系统" /></el-form-item></div>
              <el-form-item label="需求描述"><el-input v-model="structuredForm.problem_statement" type="textarea" :rows="4" resize="none" /></el-form-item>
              <div class="cols"><el-form-item label="目标用户"><el-input v-model="structuredForm.target_users" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="用户痛点"><el-input v-model="structuredForm.user_pain_points" type="textarea" :rows="3" resize="none" /></el-form-item></div>
              <div class="cols"><el-form-item label="核心场景"><el-input v-model="structuredForm.key_scenarios" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="核心功能"><el-input v-model="structuredForm.core_features" type="textarea" :rows="3" resize="none" /></el-form-item></div>
              <div class="cols"><el-form-item label="页面偏好"><el-input v-model="structuredForm.primary_pages_hint" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="重点演示场景"><el-input v-model="structuredForm.demo_focus" type="textarea" :rows="3" resize="none" /></el-form-item></div>
              <div class="cols"><el-form-item label="页面数量偏好"><el-input v-model="structuredForm.page_count_preference" /></el-form-item><el-form-item label="界面偏好"><el-input v-model="structuredForm.feature_preferences" /></el-form-item></div>
              <div class="cols"><el-form-item label="原型风格"><el-select v-model="structuredForm.tech_stack" class="full"><el-option v-for="option in styleOptions" :key="`${option.label}-structured`" :label="option.label" :value="option.value" /></el-select></el-form-item><el-form-item label="约束条件"><el-input v-model="structuredForm.constraints" /></el-form-item></div>
              <el-form-item label="补充说明"><el-input v-model="structuredForm.delivery_notes" type="textarea" :rows="4" resize="none" /></el-form-item>
            </el-form>
          </div>
          <div class="actions actions-grid">
            <el-button type="primary" :loading="loadingAction === 'structure'" @click="structureRequirement"><el-icon><Document /></el-icon>解析需求摘要</el-button>
            <el-button type="success" :loading="loadingAction === 'prd'" @click="generatePrd"><el-icon><Document /></el-icon>生成 PRD</el-button>
            <el-button type="warning" :loading="loadingAction === 'demo'" @click="generateDemo"><el-icon><Connection /></el-icon>生成 Demo 与原型说明</el-button>
            <el-button @click="resetAll">清空工作区</el-button>
          </div>
        </section>

        <section class="card spec-card">
          <div class="section-head"><div><h2>需求摘要 / Requirement Spec</h2><p>它是后续生成、检查和修改的唯一输入基线。</p></div></div>
          <div v-if="!hasRequirementSpec" class="empty">点击“解析需求摘要”后，这里会展示结构化结果。</div>
          <el-form v-else label-position="top" class="form-grid panel-body">
            <div class="cols"><el-form-item label="产品名称"><el-input v-model="specEditor.product_name" /></el-form-item><el-form-item label="产品类型"><el-input v-model="specEditor.product_type" /></el-form-item></div>
            <div class="cols"><el-form-item label="目标用户"><el-input v-model="specEditor.target_users" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="用户痛点"><el-input v-model="specEditor.user_pain_points" type="textarea" :rows="3" resize="none" /></el-form-item></div>
            <div class="cols"><el-form-item label="核心场景"><el-input v-model="specEditor.core_scenarios" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="关键功能"><el-input v-model="specEditor.key_features" type="textarea" :rows="3" resize="none" /></el-form-item></div>
            <div class="cols"><el-form-item label="主要页面"><el-input v-model="specEditor.primary_pages" type="textarea" :rows="3" resize="none" /></el-form-item><el-form-item label="用户流程"><el-input v-model="specEditor.user_flow" type="textarea" :rows="3" resize="none" /></el-form-item></div>
            <div class="cols"><el-form-item label="原型风格"><el-select v-model="specEditor.style_preference" class="full"><el-option v-for="option in styleOptions" :key="`${option.label}-spec`" :label="option.label" :value="option.value" /></el-select></el-form-item><el-form-item label="成功标准"><el-input v-model="specEditor.success_criteria" type="textarea" :rows="3" resize="none" /></el-form-item></div>
            <el-form-item label="约束条件"><el-input v-model="specEditor.constraints" type="textarea" :rows="3" resize="none" /></el-form-item>
          </el-form>
        </section>
      </div>

      <section class="card result-card">
        <div class="section-head">
          <div><h2>评审产出</h2><p>围绕同一份 Requirement Spec 查看 PRD、Demo、原型说明和一致性检查。</p></div>
          <div class="toolbar output-toolbar">
            <div class="tab-wrap">
              <el-radio-group v-model="outputTab" size="small">
                <el-radio-button value="prd">PRD</el-radio-button>
                <el-radio-button value="demo">Demo</el-radio-button>
                <el-radio-button value="outline">原型说明</el-radio-button>
                <el-radio-button value="consistency">一致性检查</el-radio-button>
              </el-radio-group>
            </div>
            <div class="toolbar-actions">
              <el-button type="primary" plain :loading="loadingAction === 'consistency'" @click="runConsistencyCheck">运行检查</el-button>
              <el-button v-if="currentArtifact" :icon="copied ? Check : CopyDocument" circle @click="copyCurrentArtifact" />
            </div>
          </div>
        </div>

        <div v-if="loadingAction" class="empty"><el-icon class="spin"><Connection /></el-icon><span>正在处理内容，请稍候。</span></div>
        <div v-else-if="outputTab === 'prd'" class="result-panel"><div v-if="result.prd" class="markdown-body" v-html="renderedPrd"></div><div v-else class="empty">先完成需求摘要，再生成 PRD。</div></div>
        <div v-else-if="outputTab === 'demo'" class="result-panel"><div v-if="result.demoHtml"><div class="toolbar output-toolbar"><div class="tab-wrap"><el-radio-group v-model="demoView" size="small"><el-radio-button value="preview">预览</el-radio-button><el-radio-button value="code">HTML</el-radio-button></el-radio-group></div><div class="toolbar-actions"><el-button size="small" @click="downloadDemo">下载 HTML</el-button></div></div><iframe v-if="demoView === 'preview'" :srcdoc="result.demoHtml" class="demo-frame" title="Demo preview"></iframe><pre v-else class="code-block">{{ result.demoHtml }}</pre></div><div v-else class="empty">生成 Demo 后，这里会展示可直接评审和下载的原型页面。</div></div>
        <div v-else-if="outputTab === 'outline'" class="result-panel"><div v-if="result.prototypeOutline" class="markdown-body" v-html="renderedOutline"></div><div v-else class="empty">生成 Demo 后，这里会展示页面结构、操作路径和验证目标。</div></div>
        <div v-else class="result-panel"><div v-if="result.consistency" class="consistency"><div class="score"><div><p class="muted">一致性等级</p><h3>{{ result.consistency.overall_level }}</h3></div><strong>{{ result.consistency.score }}</strong></div><div class="check-list"><article v-for="item in result.consistency.checks" :key="item.id" class="check-item"><div class="between"><h4>{{ item.label }}</h4><span :class="['chip', item.status]">{{ item.status }}</span></div><p>{{ item.summary }}</p><p v-if="item.missing.length" class="muted">缺失项：{{ item.missing.join('、') }}</p></article></div><div class="cols"><div><h4>问题列表</h4><ul v-if="result.consistency.issues.length" class="plain-list"><li v-for="issue in result.consistency.issues" :key="`${issue.title}-${issue.description}`"><strong>{{ issue.title }}</strong><span>（{{ issue.severity }}）{{ issue.description }}</span></li></ul><p v-else class="muted">当前未发现明显一致性缺口。</p></div><div><h4>修复建议</h4><div v-if="result.consistency.repair_suggestions.length" class="suggestions"><button v-for="suggestion in result.consistency.repair_suggestions" :key="suggestion" type="button" class="suggestion" @click="applyRepairSuggestion(suggestion)">{{ suggestion }}</button></div><p v-else class="muted">当前没有额外修复建议。</p></div></div></div><div v-else class="empty">点击“运行检查”后，这里会展示产物之间的一致性结果。</div></div>
      </section>
    </main>

    <section class="card feedback-card">
      <div class="section-head"><div><h2>定点修改</h2><p>先选改哪里，再补一句说明。每次返回本轮变更摘要，但不做持久化版本回滚。</p></div></div>
      <div class="cols cols-3"><el-form-item label="修改类型"><el-select v-model="iterationForm.change_type" class="full"><el-option v-for="option in changeTypeOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item><el-form-item label="目标模块"><el-select v-model="iterationForm.target_module" class="full"><el-option v-for="option in targetModuleOptions" :key="option.value" :label="option.label" :value="option.value" /></el-select></el-form-item><el-form-item label="影响页面"><el-select v-model="iterationForm.affected_pages" class="full" multiple collapse-tags collapse-tags-tooltip><el-option v-for="page in pageOptions" :key="page" :label="page" :value="page" /></el-select></el-form-item></div>
      <el-form-item label="修改说明"><el-input v-model="iterationForm.instruction" type="textarea" :rows="4" resize="none" placeholder="例如：增加一个评审结果页，把关键问题和修复建议集中展示；Demo 里需要从总览页点击进入结果页。" /></el-form-item>
      <div v-if="result.changeSummary" class="check-item"><p><strong>本轮变更</strong></p><p>{{ result.changeSummary }}</p><p v-if="result.changedSections.length" class="muted">改动区域：{{ result.changedSections.join('、') }}</p><p v-if="result.affectedPages.length" class="muted">影响页面：{{ result.affectedPages.join('、') }}</p></div>
      <div class="actions feedback-actions"><el-button type="primary" :loading="loadingAction === 'iterate-prd'" @click="iteratePrd">更新 PRD</el-button><el-button type="success" :loading="loadingAction === 'iterate-demo'" @click="iterateDemo">更新 Demo</el-button></div>
    </section>

    <el-dialog v-model="modelConfigVisible" title="模型配置" width="760px" class="model-dialog">
      <p class="dialog-copy">在这里切换模型平台、模型名称和接口配置。设置只保存在当前浏览器。</p>
      <el-form label-position="top" class="form-grid">
        <div class="cols">
          <el-form-item label="模型平台">
            <el-select v-model="modelConfig.provider" class="full">
              <el-option v-for="provider in modelOptions" :key="provider.id" :label="provider.label" :value="provider.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="模型名称">
            <el-select v-model="modelConfig.model" class="full" filterable allow-create default-first-option>
              <el-option v-for="model in currentModelChoices" :key="model.id" :label="model.label" :value="model.id" />
            </el-select>
          </el-form-item>
        </div>
        <div class="cols">
          <el-form-item label="API Key">
            <el-input v-model="modelConfig.api_key" show-password :placeholder="providerRequiresApiKey ? '输入你自己的 API Key；若后端已配置默认 Key，这里可留空' : '本地 Ollama 模式可留空，系统会自动使用占位 Key'" />
          </el-form-item>
          <el-form-item label="Base URL">
            <el-input v-model="modelConfig.base_url" placeholder="兼容 OpenAI 的接口地址，例如 https://api.deepseek.com/v1" />
          </el-form-item>
        </div>
        <div class="cols">
          <el-form-item label="Max Tokens">
            <el-input v-model="maxTokensInput" class="full" placeholder="留空则自动" inputmode="numeric" clearable />
          </el-form-item>
          <el-form-item label="连接状态">
            <div class="config-status">{{ modelStatusText }}</div>
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-actions">
          <el-button @click="resetModelConfig">恢复默认</el-button>
          <el-button type="primary" plain :loading="testingModel" @click="testModelConnection">测试连接</el-button>
          <el-button type="primary" @click="modelConfigVisible = false">完成</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-shell { max-width: 1480px; margin: 0 auto; padding: 32px 24px 40px; }
.hero { margin-bottom: 24px; padding: 28px 30px; border-radius: 28px; border: 1px solid rgba(27, 44, 42, 0.08); background: linear-gradient(135deg, rgba(255, 246, 235, 0.94), rgba(245, 251, 249, 0.94)); box-shadow: 0 20px 46px rgba(45, 63, 58, 0.08); }
.hero-top { display: flex; gap: 20px; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }
.hero-copy-block { flex: 1 1 760px; min-width: 0; }
.hero-side { display: grid; gap: 12px; min-width: min(100%, 280px); }
.eyebrow { margin: 0 0 8px; color: var(--accent-700); font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; }
.hero h1 { margin: 0; font-size: clamp(2rem, 4vw, 3.1rem); line-height: 1.05; }
.hero-copy { margin: 14px 0 0; max-width: 980px; color: var(--ink-700); line-height: 1.8; }
.config-pill { display: grid; gap: 4px; padding: 16px 18px; border-radius: 20px; background: rgba(255, 255, 255, 0.76); border: 1px solid rgba(27, 44, 42, 0.08); }
.pill-label { font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-500); }
.config-pill strong { color: var(--ink-900); font-size: 15px; line-height: 1.4; }
.pill-meta { color: var(--ink-600); font-size: 13px; line-height: 1.5; }
.config-trigger { width: 100%; min-height: 46px; }
.grid { display: grid; grid-template-columns: minmax(320px, 520px) minmax(0, 1fr); gap: 20px; align-items: stretch; }
.grid > * { min-width: 0; }
.stack { display: grid; gap: 20px; min-width: 0; }
.card { display: flex; flex-direction: column; gap: 18px; background: rgba(255, 251, 244, 0.92); border: 1px solid rgba(27, 44, 42, 0.1); border-radius: 24px; box-shadow: 0 18px 40px rgba(45, 63, 58, 0.08); backdrop-filter: blur(10px); padding: 24px; }
.input-card, .spec-card { min-height: 0; }
.feedback-card { margin-top: 20px; }
.section-head, .toolbar, .actions, .between { display: flex; gap: 12px; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; }
.section-head { margin-bottom: 18px; }
.section-head h2, .check-item h4 { margin: 0; }
.section-head p, .muted { color: var(--ink-600); }
.section-head > div:first-child,
.toolbar > * { min-width: 0; }
.section-head > div:first-child { flex: 1 1 280px; }
.toolbar { justify-content: flex-end; }
.output-toolbar { align-items: center; }
.tab-wrap { flex: 1 1 320px; min-width: 0; }
.toolbar-actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end; align-items: center; }
.actions { width: 100%; }
.action-row { justify-content: flex-start; }
.panel-body, .form-grid { display: grid; gap: 16px; min-width: 0; }
.actions-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.actions-grid :deep(.el-button),
.feedback-actions :deep(.el-button) { width: 100%; margin: 0; }
.actions-grid :deep(.el-button),
.feedback-actions :deep(.el-button),
.toolbar-actions :deep(.el-button),
.dialog-actions :deep(.el-button) { min-height: 44px; }
.actions-grid :deep(.el-button:not(.is-circle)),
.feedback-actions :deep(.el-button:not(.is-circle)),
.toolbar-actions :deep(.el-button:not(.is-circle)),
.dialog-actions :deep(.el-button:not(.is-circle)) { display: inline-flex; align-items: center; justify-content: center; }
.actions-grid :deep(.el-button:not(.is-circle) > span),
.feedback-actions :deep(.el-button:not(.is-circle) > span),
.toolbar-actions :deep(.el-button:not(.is-circle) > span),
.dialog-actions :deep(.el-button:not(.is-circle) > span) { display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; }
.feedback-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.cols { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.full { width: 100%; }
.config-status { min-height: 46px; display: flex; align-items: center; padding: 10px 12px; border-radius: 14px; border: 1px dashed rgba(27, 44, 42, 0.14); color: var(--ink-700); background: rgba(255, 255, 255, 0.55); line-height: 1.6; }
.result-card { min-height: 0; min-width: 0; height: 100%; }
.result-panel { min-height: 700px; flex: 1; }
.empty { min-height: 220px; display: flex; align-items: center; justify-content: center; text-align: center; border: 1px dashed rgba(27, 44, 42, 0.14); border-radius: 18px; background: rgba(255, 255, 255, 0.65); color: var(--ink-600); padding: 20px; }
.result-card > .empty { flex: 1; }
.spin { font-size: 32px; margin-right: 10px; animation: spin 1.6s linear infinite; }
.markdown-body { line-height: 1.8; color: var(--ink-900); }
.markdown-body :deep(h1) { margin-top: 0; padding-bottom: 12px; border-bottom: 2px solid rgba(219, 109, 47, 0.2); }
.markdown-body :deep(table) { width: 100%; border-collapse: collapse; margin: 18px 0; }
.markdown-body :deep(th), .markdown-body :deep(td) { border: 1px solid rgba(27, 44, 42, 0.12); padding: 10px 12px; text-align: left; }
.markdown-body :deep(th) { background: rgba(42, 157, 143, 0.08); }
.code-block, .markdown-body :deep(pre) { background: #16211f; color: #e7f0ee; border-radius: 18px; padding: 18px; overflow: auto; font-family: 'IBM Plex Mono', Consolas, monospace; font-size: 13px; line-height: 1.7; }
.demo-frame { width: 100%; min-height: 620px; border: 1px solid rgba(27, 44, 42, 0.12); border-radius: 18px; background: #fff; }
.consistency, .check-list { display: grid; gap: 14px; }
.score, .check-item { border: 1px solid rgba(27, 44, 42, 0.1); background: rgba(255, 255, 255, 0.75); border-radius: 18px; padding: 16px 18px; }
.score { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, rgba(219,109,47,0.12), rgba(42,157,143,0.12)); }
.score strong { font-size: 2.2rem; color: var(--accent-700); }
.chip { display: inline-flex; min-width: 68px; justify-content: center; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.chip.pass { background: rgba(42,157,143,0.14); color: #1f6f64; }
.chip.warning { background: rgba(255,183,77,0.18); color: #9c6400; }
.chip.fail { background: rgba(219,109,47,0.16); color: #a44912; }
.plain-list { padding-left: 18px; }
.plain-list li + li { margin-top: 10px; }
.suggestions { display: flex; flex-wrap: wrap; gap: 10px; }
.suggestion { border: 1px solid rgba(27, 44, 42, 0.12); border-radius: 999px; background: rgba(255,255,255,0.85); padding: 10px 14px; cursor: pointer; }
.dialog-copy { margin: 0 0 18px; color: var(--ink-600); line-height: 1.7; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px; flex-wrap: wrap; }
:deep(.el-form-item__label) { font-weight: 600; color: var(--ink-800); }
:deep(.el-form-item) { margin-bottom: 0; }
:deep(.el-input__wrapper), :deep(.el-textarea__inner), :deep(.el-select__wrapper) { border-radius: 14px; box-shadow: inset 0 0 0 1px rgba(27, 44, 42, 0.08); }
:deep(.el-input__wrapper), :deep(.el-select__wrapper), :deep(.el-input-number), :deep(.el-radio-button__inner) { min-height: 44px; }
:deep(.el-textarea__inner) { min-height: 112px; }
:deep(.el-input-number) { width: 100%; }
:deep(.el-radio-group) { max-width: 100%; display: flex; flex-wrap: wrap; gap: 8px; }
:deep(.el-radio-button__inner) { white-space: nowrap; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@media (max-width: 1240px) { .grid { grid-template-columns: 1fr; } .result-card, .input-card, .spec-card { min-height: 0; height: auto; } }
@media (max-width: 900px) { .cols, .cols-3, .actions-grid, .feedback-actions { grid-template-columns: 1fr; } .hero { padding: 24px 22px; } }
@media (max-width: 768px) { .page-shell { padding: 20px 16px 28px; } .section-head, .toolbar, .actions, .between, .dialog-actions { flex-direction: column; align-items: stretch; } .hero-side { width: 100%; } .demo-frame { min-height: 440px; } .result-panel { min-height: 0; } }
</style>
