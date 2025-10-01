<template>
  <div class="pa-6">
    <v-row>
      <v-col md="8" offset-md="2">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            可视化分析中心
          </v-card-title>
          <v-card-text>
            <p>请选择您要使用的分析功能：</p>
            <v-list>
              <v-list-item to="/visual-analysis/inter-field">
                <v-list-item-icon>
                  <v-icon>mdi-chart-bar</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>跨田块长势对比</v-list-item-title>
                  <v-list-item-subtitle>同时期内，不同田块的各项指标对比</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item to="/visual-analysis/intra-field">
                <v-list-item-icon>
                  <v-icon>mdi-chart-line</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>单田块长势追踪</v-list-item-title>
                  <v-list-item-subtitle>同一田块，不同时期各项指标的变化趋势</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'VisualAnalysis',
});
</script>
