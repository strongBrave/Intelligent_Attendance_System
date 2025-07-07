<template>
  <div class="department-detail-container">
    <!-- 页面标题和当前时间 -->
    <div class="page-header">
      <div class="header-left">
        <div class="breadcrumb">
          <el-button link @click="$router.push('/dashboard')">
            <el-icon><ArrowLeft /></el-icon>
            返回仪表盘
          </el-button>
          <el-divider direction="vertical" />
          <h1>{{ department?.name }} - 考勤详情</h1>
        </div>
        <div class="current-time">
          <el-icon><Clock /></el-icon>
          <span>{{ currentDateTime }}</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 部门统计信息 -->
    <div class="stats-cards" v-if="attendanceDetail">
      <el-card class="stat-card total">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.total_employees }}</div>
            <div class="stat-label">部门总人数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card sign-in">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.sign_in_count }}</div>
            <div class="stat-label">正常签到</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card sign-out">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.sign_out_count }}</div>
            <div class="stat-label">正常签退</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card late">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.late_count }}</div>
            <div class="stat-label">迟到</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card early-leave">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><ArrowDown /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.early_leave_count }}</div>
            <div class="stat-label">早退</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card late-leave">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><ArrowRight /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.late_leave_count || 0 }}</div>
            <div class="stat-label">晚退</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card absent">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><Close /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.absent_count }}</div>
            <div class="stat-label">缺勤</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card not-signed-in">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.not_signed_in_count }}</div>
            <div class="stat-label">未签到</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card not-signed-out">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ attendanceDetail.summary.not_signed_out_count }}</div>
            <div class="stat-label">未签退</div>
          </div>
        </div>
      </el-card>
    </div>


    <!-- 考勤数据展示 -->
    <div class="attendance-sections">
      <!-- 签到相关记录 -->
      <el-card class="attendance-group-card">
        <template #header>
          <div class="group-header">
            <span class="group-title">
              <el-icon><Clock /></el-icon>
              签到相关记录
            </span>
            <span class="group-subtitle">包括正常签到、迟到、缺勤、未签到等记录</span>
          </div>
        </template>

        <div class="group-sections">
          <!-- 正常签到记录 -->
          <el-card class="attendance-section sign-in-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Clock /></el-icon>
              正常签到 ({{ attendanceDetail?.sign_in_records?.length || 0 }})
            </span>
            <el-tag type="primary" size="small" class="sign-in-tag">今日</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.sign_in_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
          class="sign-in-table"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="晚退" value="late_leave" />
                  <el-option label="缺勤" value="absent" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span>{{ scope.row.remark || '无备注' }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.sign_in_records || attendanceDetail.sign_in_records.length === 0)" 
          description="暂无正常签到记录" 
          :image-size="80"
        />
      </el-card>



      <!-- 迟到记录 -->
      <el-card class="attendance-section late-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Warning /></el-icon>
              迟到记录 ({{ attendanceDetail?.late_records?.length || 0 }})
            </span>
            <el-tag type="warning" size="small" class="late-tag">迟到</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.late_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
          class="late-table"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center" />
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="晚退" value="late_leave" />
                  <el-option label="缺勤" value="absent" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span>{{ scope.row.remark || '无备注' }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.late_records || attendanceDetail.late_records.length === 0)" 
          description="暂无迟到记录" 
          :image-size="80"
        />
      </el-card>





      <!-- 缺勤记录 -->
      <el-card class="attendance-section absent-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><Close /></el-icon>
              缺勤记录 ({{ attendanceDetail?.absent_records?.length || 0 }})
            </span>
            <el-tag type="danger" size="small" class="absent-tag">缺勤</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.absent_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
          class="absent-table"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center">
            <template #default="scope">
              <span style="color: #909399;">未签到</span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span style="color: #909399;">无位置信息</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <!-- 缺勤记录（没有id）只能补录签到相关状态 -->
                  <template v-if="!scope.row.id">
                    <el-option label="正常签到" value="normal" />
                    <el-option label="迟到" value="late" />
                    <el-option label="缺勤" value="absent" />
                  </template>
                  <!-- 已存在的记录可以修改为所有状态 -->
                  <template v-else>
                    <el-option label="正常" value="normal" />
                    <el-option label="迟到" value="late" />
                    <el-option label="早退" value="early_leave" />
                    <el-option label="晚退" value="late_leave" />
                    <el-option label="缺勤" value="absent" />
                  </template>
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
                      <el-table-column label="备注" min-width="200">
              <template #default="scope">
                <span style="color: #909399;">{{ scope.row.remark || '缺勤' }}</span>
              </template>
            </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.absent_records || attendanceDetail.absent_records.length === 0)" 
          description="暂无缺勤记录" 
          :image-size="80"
        />
      </el-card>

      <!-- 未签到记录 -->
      <el-card class="attendance-section not-signed-in-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><User /></el-icon>
              未签到记录 ({{ attendanceDetail?.not_signed_in_records?.length || 0 }})
            </span>
            <el-tag type="warning" size="small" class="not-signed-in-tag">未签到</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.not_signed_in_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
          class="not-signed-in-table"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="time" label="签到时间" width="180" align="center">
            <template #default="scope">
              <span style="color: #909399;">未签到</span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span style="color: #909399;">无位置信息</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常签到" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="缺勤" value="absent" />
                  <el-option label="未签到" value="not_signed_in" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="200">
            <template #default="scope">
              <span style="color: #909399;">{{ scope.row.remark || '今日未签到' }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.not_signed_in_records || attendanceDetail.not_signed_in_records.length === 0)" 
          description="暂无未签到记录" 
          :image-size="80"
        />
      </el-card>
        </div>
      </el-card>

      <!-- 签退相关记录 -->
      <el-card class="attendance-group-card">
        <template #header>
          <div class="group-header">
            <span class="group-title">
              <el-icon><Timer /></el-icon>
              签退相关记录
            </span>
            <span class="group-subtitle">包括正常签退、早退、晚退、未签退等记录</span>
          </div>
        </template>

        <div class="group-sections">
          <!-- 正常签退记录 -->
          <el-card class="attendance-section sign-out-section">
            <template #header>
              <div class="section-header">
                <span class="section-title">
                  <el-icon><Timer /></el-icon>
                  正常签退 ({{ attendanceDetail?.sign_out_records?.length || 0 }})
                </span>
                <el-tag type="success" size="small" class="sign-out-tag">今日</el-tag>
              </div>
            </template>

            <el-table 
              :data="attendanceDetail?.sign_out_records || []" 
              border 
              stripe 
              v-loading="loading"
              style="width: 100%"
              class="sign-out-table"
            >
              <el-table-column prop="name" label="员工姓名" width="120" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="time" label="签退时间" width="180" align="center" />
              <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
              <el-table-column label="状态" width="150" align="center">
                <template #default="scope">
                  <div class="status-selector">
                    <el-select 
                      v-model="scope.row.status" 
                      size="small" 
                      style="width: 120px"
                      placeholder="选择状态"
                    >
                      <el-option label="正常" value="normal" />
                      <el-option label="迟到" value="late" />
                      <el-option label="早退" value="early_leave" />
                      <el-option label="晚退" value="late_leave" />
                      <el-option label="缺勤" value="absent" />
                    </el-select>
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="updateStatus(scope.row)"
                      style="margin-left: 8px"
                    >
                      更新
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="备注" min-width="150" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ scope.row.remark || '无备注' }}</span>
                </template>
              </el-table-column>
            </el-table>

            <el-empty 
              v-if="!loading && (!attendanceDetail?.sign_out_records || attendanceDetail.sign_out_records.length === 0)" 
              description="暂无正常签退记录" 
              :image-size="80"
            />
          </el-card>

          <!-- 早退记录 -->
          <el-card class="attendance-section early-leave-section">
            <template #header>
              <div class="section-header">
                <span class="section-title">
                  <el-icon><ArrowDown /></el-icon>
                  早退记录 ({{ attendanceDetail?.early_leave_records?.length || 0 }})
                </span>
                <el-tag type="danger" size="small" class="early-leave-tag">早退</el-tag>
              </div>
            </template>

            <el-table 
              :data="attendanceDetail?.early_leave_records || []" 
              border 
              stripe 
              v-loading="loading"
              style="width: 100%"
              class="early-leave-table"
            >
              <el-table-column prop="name" label="员工姓名" width="120" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="time" label="签退时间" width="180" align="center" />
              <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
              <el-table-column label="状态" width="150" align="center">
                <template #default="scope">
                  <div class="status-selector">
                    <el-select 
                      v-model="scope.row.status" 
                      size="small" 
                      style="width: 120px"
                      placeholder="选择状态"
                    >
                      <el-option label="正常" value="normal" />
                      <el-option label="迟到" value="late" />
                      <el-option label="早退" value="early_leave" />
                      <el-option label="晚退" value="late_leave" />
                      <el-option label="缺勤" value="absent" />
                    </el-select>
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="updateStatus(scope.row)"
                      style="margin-left: 8px"
                    >
                      更新
                    </el-button>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="备注" min-width="150" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ scope.row.remark || '无备注' }}</span>
                </template>
              </el-table-column>
            </el-table>

            <el-empty 
              v-if="!loading && (!attendanceDetail?.early_leave_records || attendanceDetail.early_leave_records.length === 0)" 
              description="暂无早退记录" 
              :image-size="80"
            />
          </el-card>

          <!-- 晚退记录 -->
          <el-card class="attendance-section late-leave-section">
            <template #header>
              <div class="section-header">
                <span class="section-title">
                  <el-icon><ArrowRight /></el-icon>
                  晚退记录 ({{ attendanceDetail?.late_leave_records?.length || 0 }})
                </span>
                <el-tag type="info" size="small" class="late-leave-tag">晚退</el-tag>
              </div>
            </template>

            <el-table 
              :data="attendanceDetail?.late_leave_records || []" 
              border 
              stripe 
              v-loading="loading"
              style="width: 100%"
              class="late-leave-table"
            >
              <el-table-column prop="name" label="员工姓名" width="120" />
              <el-table-column prop="phone" label="手机号" width="150" />
              <el-table-column prop="time" label="签退时间" width="180" align="center" />
              <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
              <el-table-column label="状态" width="150" align="center">
                <template #default="scope">
                  <div class="status-selector">
                    <el-select 
                      v-model="scope.row.status" 
                      size="small" 
                      style="width: 120px"
                      placeholder="选择状态"
                    >
                      <el-option label="正常" value="normal" />
                      <el-option label="迟到" value="late" />
                      <el-option label="早退" value="early_leave" />
                      <el-option label="晚退" value="late_leave" />
                      <el-option label="缺勤" value="absent" />
                    </el-select>
                    <el-button 
                      size="small" 
                      type="primary" 
                      @click="updateStatus(scope.row)"
                      style="margin-left: 8px"
                    >
                      更新
                    </el-button>
                  </div>
                                  </template>
              </el-table-column>
              <el-table-column label="备注" min-width="150" show-overflow-tooltip>
                <template #default="scope">
                  <span>{{ scope.row.remark || '无备注' }}</span>
                </template>
              </el-table-column>
            </el-table>

            <el-empty 
              v-if="!loading && (!attendanceDetail?.late_leave_records || attendanceDetail.late_leave_records.length === 0)" 
              description="暂无晚退记录" 
              :image-size="80"
            />
          </el-card>

      <!-- 未签退记录 -->
      <el-card class="attendance-section not-signed-out-section">
        <template #header>
          <div class="section-header">
            <span class="section-title">
              <el-icon><CircleClose /></el-icon>
              未签退记录 ({{ attendanceDetail?.not_signed_out_records?.length || 0 }})
            </span>
            <el-tag type="danger" size="small" class="not-signed-out-tag">未签退</el-tag>
          </div>
        </template>

        <el-table 
          :data="attendanceDetail?.not_signed_out_records || []" 
          border 
          stripe 
          v-loading="loading"
          style="width: 100%"
          class="not-signed-out-table"
        >
          <el-table-column prop="name" label="员工姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="150" />
          <el-table-column prop="sign_in_time" label="签到时间" width="180" align="center">
            <template #default="scope">
              <span style="color: #67C23A;">{{ scope.row.sign_in_time }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" min-width="150" show-overflow-tooltip />
          <el-table-column label="状态" width="150" align="center">
            <template #default="scope">
              <div class="status-selector">
                <el-select 
                  v-model="scope.row.status" 
                  size="small" 
                  style="width: 120px"
                  placeholder="选择状态"
                >
                  <el-option label="正常" value="normal" />
                  <el-option label="迟到" value="late" />
                  <el-option label="早退" value="early_leave" />
                  <el-option label="晚退" value="late_leave" />
                  <el-option label="缺勤" value="absent" />
                </el-select>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="updateStatus(scope.row)"
                  style="margin-left: 8px"
                >
                  更新
                </el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150" show-overflow-tooltip>
            <template #default="scope">
              <span>{{ scope.row.remark || '无备注' }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty 
          v-if="!loading && (!attendanceDetail?.not_signed_out_records || attendanceDetail.not_signed_out_records.length === 0)" 
          description="暂无未签退记录" 
          :image-size="80"
        />
      </el-card>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  ArrowLeft, Clock, Refresh, User, Timer, Warning, Close, 
  TrendCharts, ArrowDown, CircleClose, ArrowRight
} from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const department = ref(null)
const attendanceDetail = ref(null)
const currentDateTime = ref('')
let timeInterval = null

// 获取当前时间
const updateCurrentTime = () => {
  const now = new Date()
  currentDateTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    weekday: 'long'
  })
}

// 获取部门信息
const fetchDepartmentInfo = async () => {
  try {
    const response = await api.get(`/admin/departments/${route.params.id}`)
    department.value = response.data.department
  } catch (error) {
    console.error('获取部门信息失败:', error)
    ElMessage.error('获取部门信息失败')
  }
}

// 获取部门详细考勤数据
const fetchAttendanceDetail = async () => {
  loading.value = true
  try {
    const response = await api.get(`/admin/departments/${route.params.id}/attendance-detail`)
    attendanceDetail.value = response.data
  } catch (error) {
    console.error('获取考勤详情失败:', error)
    const errorMsg = error.response?.data?.error || '获取考勤详情失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 更新考勤状态
const updateStatus = async (record) => {
  console.log('更新状态被调用:', record)

  // 缺勤记录补录
  if (!record.id) {
    try {
      const today = attendanceDetail.value?.date || new Date().toISOString().slice(0, 10)
      const res = await api.post('/admin/attendance/makeup', {
        user_id: record.user_id,
        date: today,
        check_type: record.check_type, 
        status: record.status,
        location: record.location,
        time: record.time
      })
      ElMessage.success('补录成功')
      await fetchAttendanceDetail()
    } catch (error) {
      console.error('补录失败:', error)
      const errorMsg = error.response?.data?.error || '补录失败'
      ElMessage.error(errorMsg)
      await fetchAttendanceDetail()
    }
    return
  }

  // 正常更新
  const oldStatus = record.status
  try {
    const response = await api.put(`/admin/attendance/${record.id}/status`, {
      status: record.status
    })
    ElMessage.success('状态更新成功')
    await fetchAttendanceDetail()
  } catch (error) {
    console.error('更新状态失败:', error)
    const errorMsg = error.response?.data?.error || '更新状态失败'
    ElMessage.error(errorMsg)
    record.status = oldStatus
    await fetchAttendanceDetail()
  }
}

// 刷新数据
const refreshData = () => {
  fetchAttendanceDetail()
}



onMounted(() => {
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 1000)
  fetchDepartmentInfo()
  fetchAttendanceDetail()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.department-detail-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breadcrumb h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.current-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 8px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
  color: white;
}

.total .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sign-in .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.sign-out .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.late .stat-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.early-leave .stat-icon {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.late-leave .stat-icon {
  background: linear-gradient(135deg, #845EC2 0%, #b39ddb 100%);
}

.absent .stat-icon {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.not-signed-in .stat-icon {
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
}

.not-signed-out .stat-icon {
  background: linear-gradient(135deg, #8A2BE2 0%, #9370DB 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}

.attendance-sections {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.attendance-group-card {
  border-radius: 16px;
  box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.12);
  border: 1px solid #e4e7ed;
  background: #fff;
}

.group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.group-subtitle {
  font-size: 14px;
  color: #909399;
  font-weight: 400;
}

.group-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 16px 0;
}

.attendance-section {
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.status-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: #f5f7fa !important;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f0f0;
}

/* 各类型表格专用样式 - 对应仪表盘颜色 */

/* 签到记录 - 蓝色主题 */
.sign-in-section {
  background: linear-gradient(135deg, rgba(79, 172, 254, 0.03), rgba(0, 242, 254, 0.03));
  border: 2px solid rgba(79, 172, 254, 0.2);
  box-shadow: 0 4px 20px rgba(79, 172, 254, 0.15);
}

.sign-in-section .section-title {
  color: #4FACFE;
  font-weight: 700;
}

.sign-in-tag {
  background: linear-gradient(135deg, #4FACFE, #00F2FE);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
}

.sign-in-table {
  background: rgba(79, 172, 254, 0.02);
}

.sign-in-table :deep(.el-table__header) {
  background: rgba(79, 172, 254, 0.05);
}

.sign-in-table :deep(.el-table__row:hover) {
  background: rgba(79, 172, 254, 0.06);
}

.sign-in-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(79, 172, 254, 0.02);
}

.sign-in-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(79, 172, 254, 0.04);
}

/* 签退记录 - 绿色主题 */
.sign-out-section {
  background: linear-gradient(135deg, rgba(67, 233, 123, 0.03), rgba(56, 249, 215, 0.03));
  border: 2px solid rgba(67, 233, 123, 0.2);
  box-shadow: 0 4px 20px rgba(67, 233, 123, 0.15);
}

.sign-out-section .section-title {
  color: #43E97B;
  font-weight: 700;
}

.sign-out-tag {
  background: linear-gradient(135deg, #43E97B, #38F9D7);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(67, 233, 123, 0.3);
}

.sign-out-table {
  background: rgba(67, 233, 123, 0.02);
}

.sign-out-table :deep(.el-table__header) {
  background: rgba(67, 233, 123, 0.05);
}

.sign-out-table :deep(.el-table__row:hover) {
  background: rgba(67, 233, 123, 0.06);
}

.sign-out-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(67, 233, 123, 0.02);
}

.sign-out-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(67, 233, 123, 0.04);
}

/* 迟到记录 - 橙色主题 */
.late-section {
  background: linear-gradient(135deg, rgba(250, 112, 154, 0.03), rgba(254, 225, 64, 0.03));
  border: 2px solid rgba(250, 112, 154, 0.2);
  box-shadow: 0 4px 20px rgba(250, 112, 154, 0.15);
}

.late-section .section-title {
  color: #FA709A;
  font-weight: 700;
}

.late-tag {
  background: linear-gradient(135deg, #FA709A, #FEE140);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(250, 112, 154, 0.3);
}

.late-table {
  background: rgba(250, 112, 154, 0.02);
}

.late-table :deep(.el-table__header) {
  background: rgba(250, 112, 154, 0.05);
}

.late-table :deep(.el-table__row:hover) {
  background: rgba(250, 112, 154, 0.06);
}

.late-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(250, 112, 154, 0.02);
}

.late-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(250, 112, 154, 0.04);
}

/* 早退记录 - 红色主题 */
.early-leave-section {
  background: linear-gradient(135deg, rgba(255, 154, 158, 0.03), rgba(254, 207, 239, 0.03));
  border: 2px solid rgba(255, 154, 158, 0.2);
  box-shadow: 0 4px 20px rgba(255, 154, 158, 0.15);
}

.early-leave-section .section-title {
  color: #FF9A9E;
  font-weight: 700;
}

.early-leave-tag {
  background: linear-gradient(135deg, #FF9A9E, #FECFEF);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(255, 154, 158, 0.3);
}

.early-leave-table {
  background: rgba(255, 154, 158, 0.02);
}

.early-leave-table :deep(.el-table__header) {
  background: rgba(255, 154, 158, 0.05);
}

.early-leave-table :deep(.el-table__row:hover) {
  background: rgba(255, 154, 158, 0.06);
}

.early-leave-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(255, 154, 158, 0.02);
}

.early-leave-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(255, 154, 158, 0.04);
}

/* 晚退记录 - 紫色主题 */
.late-leave-section {
  background: linear-gradient(135deg, rgba(132, 94, 194, 0.03), rgba(179, 157, 219, 0.03));
  border: 2px solid rgba(132, 94, 194, 0.2);
  box-shadow: 0 4px 20px rgba(132, 94, 194, 0.15);
}

.late-leave-section .section-title {
  color: #845EC2;
  font-weight: 700;
}

.late-leave-tag {
  background: linear-gradient(135deg, #845EC2, #B39DDB);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(132, 94, 194, 0.3);
}

.late-leave-table {
  background: rgba(132, 94, 194, 0.02);
}

.late-leave-table :deep(.el-table__header) {
  background: rgba(132, 94, 194, 0.05);
}

.late-leave-table :deep(.el-table__row:hover) {
  background: rgba(132, 94, 194, 0.06);
}

.late-leave-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(132, 94, 194, 0.02);
}

.late-leave-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(132, 94, 194, 0.04);
}

/* 缺勤记录 - 深红色主题 */
.absent-section {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.03), rgba(238, 90, 36, 0.03));
  border: 2px solid rgba(255, 107, 107, 0.2);
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.15);
}

.absent-section .section-title {
  color: #FF6B6B;
  font-weight: 700;
}

.absent-tag {
  background: linear-gradient(135deg, #FF6B6B, #EE5A24);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
}

.absent-table {
  background: rgba(255, 107, 107, 0.02);
}

.absent-table :deep(.el-table__header) {
  background: rgba(255, 107, 107, 0.05);
}

.absent-table :deep(.el-table__row:hover) {
  background: rgba(255, 107, 107, 0.06);
}

.absent-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(255, 107, 107, 0.02);
}

.absent-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(255, 107, 107, 0.04);
}

/* 未签到记录 - 黄色主题 */
.not-signed-in-section {
  background: linear-gradient(135deg, rgba(255, 234, 167, 0.03), rgba(250, 177, 160, 0.03));
  border: 2px solid rgba(255, 234, 167, 0.2);
  box-shadow: 0 4px 20px rgba(255, 234, 167, 0.15);
}

.not-signed-in-section .section-title {
  color: #FFEAA7;
  font-weight: 700;
}

.not-signed-in-tag {
  background: linear-gradient(135deg, #FFEAA7, #FAB1A0);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(255, 234, 167, 0.3);
}

.not-signed-in-table {
  background: rgba(255, 234, 167, 0.02);
}

.not-signed-in-table :deep(.el-table__header) {
  background: rgba(255, 234, 167, 0.05);
}

.not-signed-in-table :deep(.el-table__row:hover) {
  background: rgba(255, 234, 167, 0.06);
}

.not-signed-in-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(255, 234, 167, 0.02);
}

.not-signed-in-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(255, 234, 167, 0.04);
}

/* 未签退记录 - 紫色主题 */
.not-signed-out-section {
  background: linear-gradient(135deg, rgba(138, 43, 226, 0.03), rgba(147, 112, 219, 0.03));
  border: 2px solid rgba(138, 43, 226, 0.2);
  box-shadow: 0 4px 20px rgba(138, 43, 226, 0.15);
}

.not-signed-out-section .section-title {
  color: #8A2BE2;
  font-weight: 700;
}

.not-signed-out-tag {
  background: linear-gradient(135deg, #8A2BE2, #9370DB);
  border: none;
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(138, 43, 226, 0.3);
}

.not-signed-out-table {
  background: rgba(138, 43, 226, 0.02);
}

.not-signed-out-status {
  background: linear-gradient(135deg, #8A2BE2, #9370DB);
  color: white;
  border: none;
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(138, 43, 226, 0.3);
}

.not-signed-out-table :deep(.el-table__header) {
  background: rgba(138, 43, 226, 0.05);
}

.not-signed-out-table :deep(.el-table__row:hover) {
  background: rgba(138, 43, 226, 0.06);
}

.not-signed-out-table :deep(.el-table__row:nth-child(odd)) {
  background: rgba(138, 43, 226, 0.02);
}

.not-signed-out-table :deep(.el-table__row:nth-child(even)) {
  background: rgba(138, 43, 226, 0.04);
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .attendance-sections {
    gap: 24px;
  }

  .group-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .group-title {
    font-size: 18px;
  }

  .group-sections {
    gap: 16px;
  }
}
</style> 