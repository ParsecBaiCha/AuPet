<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { studentApi } from '../../api/student'

const router = useRouter()
const userStore = useUserStore()

const pet = ref({
  name: '',
  type: '',
  level: '',
  exp: 0,
  maxExp: 0,
  health: 0,
  hunger: 0,
  happiness: 0,
  adoptDate: '',
})

const selectedItem = ref<any>(null)
const showConfirmDialog = ref(false)

const foodItems = ref<any[]>([])

const goToChat = () => { router.push('/student/ai-companion') }

const selectItem = (item: any) => { selectedItem.value = item; showConfirmDialog.value = true }
const cancelPurchase = () => { showConfirmDialog.value = false; selectedItem.value = null }

const confirmPurchase = async () => {
  if (!selectedItem.value) return
  const item = selectedItem.value
  try {
    await studentApi.buyItem(item.id)
    // 购买成功后更新本地积分与经验显示
    userStore.spendPoints(item.price)
    userStore.addExp(item.exp)
    pet.value.exp = userStore.petExp
    pet.value.maxExp = userStore.petMaxExp
    alert(`购买成功！\n\n${item.name} x1\n消耗积分：${item.price}\n获得经验：+${item.exp}\n\n💰 剩余积分：${userStore.userPoints}\n📈 经验值：${userStore.petExp}/${userStore.petMaxExp}`)
  } catch (e) {
    // 购买失败，错误提示由全局拦截器处理
  }
  showConfirmDialog.value = false
  selectedItem.value = null
}

onMounted(async () => {
  try {
    const data: any = await studentApi.getMyPet()
    if (data) {
      // 填充全局学生/宠物信息（字段名适配映射在 store 内完成）
      userStore.applyMyPet(data)
      if (data.pet) {
        const p = data.pet
        pet.value = {
          name: p.name ?? '',
          type: p.type ?? '',
          level: p.level ?? '',
          exp: p.exp ?? 0,
          maxExp: p.maxExp ?? 0,
          health: p.health ?? 0,
          hunger: p.hunger ?? 0,
          happiness: p.happiness ?? 0,
          adoptDate: p.adoptDate ?? '',
        }
      }
      if (Array.isArray(data.shopItems)) {
        foodItems.value = data.shopItems
      }
    }
  } catch (e) {
    // API 失败时保持页面可用
  }
})
</script>

<template>
<div class="my-pet">
  <div class="content-wrapper">
    <!-- Left Panel: Student Card + Pet Details -->
    <div class="left-panel">
      <div class="student-card">
        <img class="avatar" :src="userStore.studentInfo.avatar" alt="avatar" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
        <h3>{{ userStore.studentInfo.name }}</h3>
        <p class="class-name">{{ userStore.studentInfo.class }}</p>
        <div class="student-stats">
          <div class="stat"><span class="stat-value">{{ userStore.userPoints }}</span><span class="stat-label">总积分</span></div>
          <div class="stat"><span class="stat-value">{{ userStore.completedTasks }}</span><span class="stat-label">完成任务</span></div>
          <div class="stat"><span class="stat-value">{{ userStore.rank }}</span><span class="stat-label">班级排名</span></div>
        </div>
      </div>

      <div class="pet-details">
        <h3>宠物档案</h3>
        <div class="detail-item"><span class="detail-label">名字：</span><span class="detail-value">{{ pet.name }}</span></div>
        <div class="detail-item"><span class="detail-label">等级：</span><span class="detail-value level">{{ pet.level }}</span></div>
        <div class="detail-item"><span class="detail-label">领养日期：</span><span class="detail-value">{{ pet.adoptDate }}</span></div>
        <div class="detail-item">
          <span class="detail-label">健康值：</span>
          <div class="mini-bar"><div class="mini-fill" :style="{ width: pet.health + '%', background: '#81c784' }"></div></div>
          <span class="detail-value">{{ pet.health }}%</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">饱食度：</span>
          <div class="mini-bar"><div class="mini-fill" :style="{ width: pet.hunger + '%', background: 'rgba(255, 140, 0, 0.5)' }"></div></div>
          <span class="detail-value">{{ pet.hunger }}%</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">快乐度：</span>
          <div class="mini-bar"><div class="mini-fill" :style="{ width: pet.happiness + '%', background: '#f48fb1' }"></div></div>
          <span class="detail-value">{{ pet.happiness }}%</span>
        </div>
      </div>
    </div>

    <!-- Center Panel: Pet Display -->
    <div class="center-panel">
      <div class="pet-display">
        <div class="exp-bar">
          <div class="exp-label">经验值</div>
          <div class="exp-bar-container">
            <div class="exp-fill" :style="{ width: (pet.exp / pet.maxExp * 100) + '%' }"></div>
          </div>
          <div class="exp-text">{{ pet.exp }} / {{ pet.maxExp }}</div>
        </div>

        <div class="pet-box">
          <div class="pet-container">
            <img class="pet-sprite" :src="pet.type" alt="pet" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          </div>
          <div class="pet-animation">
            <div class="shadow"></div>
          </div>
        </div>

        <div class="pet-footer">
          <span class="pet-name-label">{{ pet.name }}</span>
          <button @click="goToChat" class="chat-btn">和宠物聊天</button>
        </div>
      </div>
    </div>

    <!-- Right Panel: Mall -->
    <div class="right-panel">
      <div class="mall-header">
        <img class="mall-icon" src="/images/Student_Icons/Mall.jpg" />
        <div class="points-display">
          <img class="points-icon" src="/images/Student_Icons/points.svg" />
          <span>{{ userStore.userPoints }}</span>
        </div>
      </div>
      <div class="mall-items">
        <div v-for="item in foodItems" :key="item.id" class="mall-item" @click="selectItem(item)">
          <img class="item-image" :src="item.image" :alt="item.name" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          <div class="item-name">{{ item.name }}</div>
          <div class="item-price">{{ item.price }}积分</div>
          <div class="item-exp">+{{ item.exp }}经验</div>
        </div>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="showConfirmDialog" class="confirm-dialog">
      <div class="dialog-overlay" @click="cancelPurchase"></div>
      <div class="dialog-content">
        <h3>确认购买</h3>
        <div class="dialog-item">
          <img class="item-image" :src="selectedItem?.image" :alt="selectedItem?.name" @error="($event.target as HTMLImageElement).src = '/images/pets/default.jpg'" />
          <div class="item-info">
            <span class="item-name">{{ selectedItem?.name }}</span>
            <span class="item-price">价格：{{ selectedItem?.price }}积分</span>
            <span class="item-exp">经验：+{{ selectedItem?.exp }}</span>
          </div>
        </div>
        <div class="dialog-buttons">
          <button class="btn-cancel" @click="cancelPurchase">取消</button>
          <button class="btn-confirm" @click="confirmPurchase">确认购买</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.my-pet { height: 100%; min-height: 620px; padding: 0; }
.content-wrapper { display: grid; grid-template-columns: 280px 1fr 320px; gap: 12px; height: 100%; align-items: stretch; }
.left-panel, .center-panel, .right-panel { background: rgba(255, 250, 235, 0.98); border-radius: 5px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15); display: flex; flex-direction: column; overflow: hidden; }
.left-panel { padding: 8px; }
.student-card { border-radius: 15px; padding: 25px; text-align: center; flex-shrink: 0; }
.avatar { width: 80px; height: 80px; object-fit: cover; margin-bottom: 15px; border-radius: 50%; border: 3px solid rgba(255, 140, 0, 0.5); }
.student-card h3 { color: #333; margin-bottom: 5px; }
.class-name { color: #999; font-size: 14px; margin-bottom: 20px; }
.student-stats { display: flex; justify-content: space-around; padding-top: 15px; border-top: 1px solid #eee; }
.stat { display: flex; flex-direction: column; gap: 5px; }
.stat-value { font-size: 20px; font-weight: bold; color: #8985cf; }
.stat-label { font-size: 12px; color: #999; }
.pet-details { border-radius: 5px; padding: 25px; margin-top: 20px; flex: 1; display: flex; flex-direction: column; }
.pet-details h3 { color: #8985cf; margin-bottom: 20px; font-size: 18px; }
.detail-item { display: flex; align-items: center; gap: 10px; margin-bottom: 15px; }
.detail-label { color: #666; font-size: 14px; width: 80px; }
.detail-value { color: #333; font-weight: 500; }
.detail-value.level { color: #f4bb6e; }
.mini-bar { flex: 1; height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; }
.mini-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.center-panel { padding: 16px; }
.pet-display { display: flex; flex-direction: column; align-items: center; flex: 1; min-height: 0; }
.exp-bar { width: 100%; margin-bottom: 20px; }
.exp-label { font-size: 14px; color: #666; margin-bottom: 10px; text-align: left; }
.exp-bar-container { height: 20px; background: #e0e0e0; border-radius: 10px; overflow: hidden; margin-bottom: 10px; }
.exp-fill { height: 100%; background: linear-gradient(90deg, #8985cf 0%, #acb6f3 100%); border-radius: 10px; transition: width 0.5s ease; }
.exp-text { text-align: right; font-size: 14px; color: #8985cf; font-weight: 500; }
.pet-box { background: white; border-radius: 5px; padding: 16px 20px; width: 90%; flex: 1; display: flex; flex-direction: column; align-items: center; border: 4px solid rgba(255, 140, 0, 0.5); min-height: 0; }
.pet-container { position: relative; flex: 1; display: flex; align-items: center; justify-content: center; }
.pet-sprite { max-width: 80%; max-height: 80%; object-fit: contain; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-25px); } }
.pet-footer { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 12px; }
.pet-name-label { background: rgba(255, 140, 0, 0.5); color: white; padding: 0px 15px; border-radius: 5px; font-size: 14px; font-weight: bold; }
.pet-animation { height: 40px; position: relative; margin-top: 5px; }
.shadow { width: 180px; height: 40px; background: rgba(0, 0, 0, 0.25); border-radius: 50%; position: absolute; left: 50%; top: -50px; transform: translateX(-50%); animation: shadow-pulse 3s ease-in-out infinite; }
@keyframes shadow-pulse { 0%, 100% { transform: translateX(-50%) scale(1); opacity: 0.3; } 50% { transform: translateX(-50%) scale(0.7); opacity: 0.1; } }
.chat-btn { margin-top: 6px; padding: 12px 24px; background: #8985cf; color: white; border: none; border-radius: 30px; font-size: 16px; cursor: pointer; transition: all 0.3s ease; }
.chat-btn:hover { transform: scale(1.05); box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25); }
.right-panel { padding: 16px; display: flex; flex-direction: column; }
.mall-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 2px solid white; flex-shrink: 0; }

.mall-icon { width: 160px; height: 80px; object-fit: contain; border-radius: 4px; }
.points-display { display: flex; align-items: center; gap: 6px; background: #f4bb6e; padding: 8px 15px; border-radius: 20px; color: white; font-weight: bold; }
.points-icon { width: 20px; height: 20px; object-fit: contain; filter: brightness(0) invert(1); }
.mall-items { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; overflow-y: auto; flex: 1; padding-right: 5px; }
.mall-items::-webkit-scrollbar { width: 6px; }
.mall-items::-webkit-scrollbar-track { background: white; border-radius: 3px; }
.mall-items::-webkit-scrollbar-thumb { background: #8985cf; border-radius: 3px; }
.mall-item { background: white; border-radius: 12px; padding: 15px; text-align: center; cursor: pointer; transition: all 0.3s ease; border: 2px solid white; }
.mall-item:hover { border-color: #8985cf; transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
.item-image { width: 60px; height: 60px; object-fit: cover; border-radius: 8px; margin-bottom: 8px; }
.item-name { font-size: 13px; color: #333; margin-bottom: 5px; }
.item-price { font-size: 11px; color: #f48d45; font-weight: bold; }
.item-exp { font-size: 10px; color: #8985cf; font-weight: 500; }
.confirm-dialog { position: fixed; top: 0; left: 0; right: 0; bottom: 0; display: flex; align-items: center; justify-content: center; z-index: 2000; }
.dialog-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); }
.dialog-content { position: relative; background: rgba(255, 250, 235, 0.98); border-radius: 20px; padding: 30px; width: 350px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); }
.dialog-content h3 { color: #f48d45; margin-bottom: 20px; text-align: center; font-size: 20px; }
.dialog-item { display: flex; align-items: center; gap: 15px; padding: 20px; background: white; border-radius: 15px; margin-bottom: 25px; }
.dialog-item .item-image { width: 80px; height: 80px; object-fit: cover; border-radius: 10px; }
.dialog-item .item-info { display: flex; flex-direction: column; gap: 5px; }
.dialog-item .item-name { font-size: 18px; color: #333; font-weight: bold; }
.dialog-item .item-price { font-size: 14px; color: #f48d45; }
.dialog-item .item-exp { font-size: 13px; color: #8985cf; }
.dialog-buttons { display: flex; gap: 15px; }
.btn-cancel, .btn-confirm { flex: 1; padding: 14px; border: none; border-radius: 12px; font-size: 16px; cursor: pointer; transition: all 0.3s ease; }
.btn-cancel { background: #e0e0e0; color: #666; }
.btn-cancel:hover { background: #d0d0d0; }
.btn-confirm { background: linear-gradient(135deg, #8985cf 0%, #acb6f3 100%); color: white; }
.btn-confirm:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2); }
@media (max-width: 1200px) { .content-wrapper { grid-template-columns: 1fr; } .left-panel, .right-panel { order: 2; } .center-panel { order: 1; } .right-panel { max-height: none; } .mall-items { max-height: 400px; } }
</style>
