<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">Page Not Found</h1>
      <p class="error-message">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div class="error-actions">
        <router-link to="/dashboard" class="btn btn-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          Go to Dashboard
        </router-link>
        <router-link to="/" class="btn btn-secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          Back to Home
        </router-link>
      </div>
    </div>

    <div class="radar-illustration">
      <svg viewBox="0 0 200 200" fill="none">
        <!-- Radar circles -->
        <circle cx="100" cy="100" r="80" stroke="currentColor" stroke-width="1" opacity="0.1" />
        <circle cx="100" cy="100" r="60" stroke="currentColor" stroke-width="1" opacity="0.1" />
        <circle cx="100" cy="100" r="40" stroke="currentColor" stroke-width="1" opacity="0.1" />
        <circle cx="100" cy="100" r="20" stroke="currentColor" stroke-width="1" opacity="0.1" />

        <!-- Cross lines -->
        <line x1="20" y1="100" x2="180" y2="100" stroke="currentColor" stroke-width="1" opacity="0.1" />
        <line x1="100" y1="20" x2="100" y2="180" stroke="currentColor" stroke-width="1" opacity="0.1" />

        <!-- Sweep -->
        <line
          x1="100"
          y1="100"
          x2="100"
          y2="20"
          stroke="url(#sweepGradient)"
          stroke-width="2"
          stroke-linecap="round"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 100 100"
            to="360 100 100"
            dur="4s"
            repeatCount="indefinite"
          />
        </line>

        <!-- Blip -->
        <circle cx="140" cy="60" r="4" fill="currentColor" opacity="0.6">
          <animate
            attributeName="opacity"
            values="0.6;0.2;0.6"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>

        <!-- Gradient -->
        <defs>
          <linearGradient id="sweepGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="currentColor" stop-opacity="0.8" />
            <stop offset="100%" stop-color="currentColor" stop-opacity="0" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // Redirect to home after 10 seconds if user does nothing
  const timeout = setTimeout(() => {
    router.push('/')
  }, 10000)

  // Cleanup timeout if component is unmounted
  return () => clearTimeout(timeout)
})
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 2rem;
}

.not-found-content {
  text-align: center;
}

.error-code {
  font-size: 8rem;
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.error-title {
  margin: 1rem 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
}

.error-message {
  margin: 0 0 2rem;
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 400px;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s;
}

.btn svg {
  width: 1.125rem;
  height: 1.125rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.btn-secondary:hover {
  background: var(--bg-primary);
}

.radar-illustration {
  width: 200px;
  height: 200px;
  color: var(--color-primary);
  opacity: 0.5;
}

@media (max-width: 640px) {
  .error-code {
    font-size: 5rem;
  }

  .error-title {
    font-size: 1.5rem;
  }

  .error-message {
    font-size: 1rem;
  }

  .error-actions {
    flex-direction: column;
  }

  .error-actions .btn {
    width: 100%;
    justify-content: center;
  }

  .radar-illustration {
    width: 150px;
    height: 150px;
  }
}
</style>
