<template>
  <div class="empty-state">
    <div class="empty-state-icon">
      <slot name="icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
          />
        </svg>
      </slot>
    </div>
    <h3 class="empty-state-title">{{ title }}</h3>
    <p class="empty-state-description">{{ description }}</p>
    <div v-if="$slots.action" class="empty-state-action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  title: 'No data found',
  description: 'There is nothing to display here yet.',
})
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.5rem;
  text-align: center;
}

.empty-state-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  color: var(--text-muted);
}

.empty-state-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state-title {
  margin: 0 0 0.5rem;
  color: var(--text-primary);
  font-size: 1.125rem;
  font-weight: 600;
}

.empty-state-description {
  margin: 0 0 1.5rem;
  max-width: 400px;
  color: var(--text-secondary);
  font-size: 0.9375rem;
  line-height: 1.6;
}

.empty-state-action {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}
</style>
