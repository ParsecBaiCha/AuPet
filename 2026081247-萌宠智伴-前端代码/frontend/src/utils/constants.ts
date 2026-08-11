export const PET_TYPES: Record<string, { icon: string; color: string }> = {
  '狗': { icon: '🐕', color: '#f6d365' },
  '猫': { icon: '🐈', color: '#a18cd1' },
  '熊': { icon: '🐻', color: '#84fab0' },
  '企鹅': { icon: '🐧', color: '#ff9a9e' },
  '兔': { icon: '🐇', color: '#fbc2eb' },
  '熊猫': { icon: '🐼', color: '#a6c0fe' },
}

export const EMOTIONS = [
  { value: 'happy', label: '开心', icon: '😊', color: '#52c41a' },
  { value: 'sad', label: '难过', icon: '😢', color: '#1890ff' },
  { value: 'angry', label: '生气', icon: '😠', color: '#f5222d' },
  { value: 'anxious', label: '焦虑', icon: '😰', color: '#fa8c16' },
  { value: 'calm', label: '平静', icon: '😌', color: '#722ed1' },
]

export const MOOD_LEVELS = [
  { value: 1, label: '很差', icon: '😫', color: '#f5222d' },
  { value: 2, label: '较差', icon: '😔', color: '#fa8c16' },
  { value: 3, label: '一般', icon: '😐', color: '#faad14' },
  { value: 4, label: '较好', icon: '😊', color: '#52c41a' },
  { value: 5, label: '很好', icon: '😄', color: '#389e0d' },
]

export const SEVERITY_COLORS: Record<string, string> = {
  '轻度': '#faad14', '中度': '#fa8c16', '重度': '#f5222d',
}

export const REVIEW_STATUS: Record<string, { color: string; label: string }> = {
  pending: { color: 'warning', label: '待审核' },
  approved: { color: 'success', label: '已通过' },
  rejected: { color: 'danger', label: '已驳回' },
}
