<template>
  <div style="padding:32px;max-width:700px;margin:auto;">
    <el-card>
      <div style="font-size:20px;font-weight:bold;margin-bottom:24px;">考勤统计分析</div>
      <el-form :inline="true" style="margin-bottom:20px;">
        <el-form-item label="员工ID">
          <el-input v-model="query.user_id" placeholder="员工ID" style="width:120px" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="query.department" placeholder="部门" style="width:120px" />
        </el-form-item>
        <el-form-item label="月份">
          <el-date-picker v-model="query.month" type="month" placeholder="选择月份" style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="getStats">查询</el-button>
        </el-form-item>
      </el-form>
      <div ref="chartRef" style="width:100%;height:400px;"></div>
    </el-card>
  </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import * as echarts from 'echarts'

const query = ref({ user_id: '', department: '', month: '' })
const stats = ref({})
const chartRef = ref()
let chart

const getStats = async () => {
  let params = {}
  if (query.value.user_id) params.user_id = query.value.user_id
  if (query.value.department) params.department = query.value.department
  if (query.value.month) params.month = query.value.month.toISOString().slice(0,7)
  const res = await api.get('/admin/attendance/stats', { params })
  stats.value = res.data || {}
  renderChart()
}

function renderChart() {
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: '考勤统计', left: 'center' },
    tooltip: {},
    xAxis: { type: 'category', data: ['出勤', '迟到', '缺勤', '加班'] },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: [stats.value.total || 0, stats.value.late || 0, stats.value.absent || 0, stats.value.overtime || 0],
      itemStyle: { color: '#409EFF' }
    }]
  })
}

onMounted(() => {
  getStats()
})
watch(stats, renderChart)
</script> 