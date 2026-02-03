import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Setup router guards for authentication and authorization
 */
export function setupRouterGuards(router: Router) {
  // Navigation guard to check authentication
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // Routes that don't require authentication
    const publicRoutes = ['Home', 'Login', 'Register', 'NotFound']

    // Check if route requires authentication
    const requiresAuth = !publicRoutes.includes(to.name as string)

    if (requiresAuth && !authStore.isAuthenticated) {
      // Store the intended destination for redirect after login
      const returnUrl = to.fullPath
      next({
        name: 'Login',
        query: returnUrl !== '/' ? { redirect: returnUrl } : undefined,
      })
    } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
      // Redirect authenticated users away from login/register pages
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  })

  // After each navigation, you can add analytics or other tracking
  router.afterEach((to) => {
    // Update page title
    if (to.meta.title) {
      document.title = `${to.meta.title} - RFTIP`
    } else {
      document.title = 'RFTIP - Radar Fusion Track Intelligence Platform'
    }
  })
}

/**
 * Check if user has required role
 */
export function hasRole(role: string): boolean {
  const authStore = useAuthStore()
  if (!authStore.user) return false

  // Admin has access to everything
  if (authStore.user.is_admin) return true

  // Add role-based logic here as needed
  return false
}

/**
 * Check if user has permission
 */
export function hasPermission(permission: string): boolean {
  const authStore = useAuthStore()
  if (!authStore.user) return false

  // Admin has all permissions
  if (authStore.user.is_admin) return true

  // Add permission-based logic here as needed
  return false
}
