/**
 * Logger Utility - Frontend Logging System
 *
 * Provides structured logging with different log levels and context tracking.
 * Logs are stored locally and can be exported for debugging.
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARNING = 2,
  ERROR = 3,
  CRITICAL = 4,
}

export interface LogEntry {
  timestamp: string
  level: LogLevel
  levelName: string
  message: string
  context?: Record<string, unknown>
  error?: {
    name: string
    message: string
    stack?: string
  }
  requestId?: string
  userId?: string
}

export interface LoggerConfig {
  minLevel: LogLevel
  enableConsole: boolean
  enableStorage: boolean
  storageKey: string
  maxStoredLogs: number
  enableStackTrace: boolean
}

class Logger {
  private config: LoggerConfig
  private logs: LogEntry[] = []
  private sessionId: string

  constructor(config?: Partial<LoggerConfig>) {
    this.sessionId = this.generateSessionId()
    this.config = {
      minLevel: LogLevel.INFO,
      enableConsole: true,
      enableStorage: true,
      storageKey: 'app_logs',
      maxStoredLogs: 1000,
      enableStackTrace: true,
      ...config,
    }
    this.loadLogs()
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private loadLogs(): void {
    if (!this.config.enableStorage) return

    try {
      const stored = localStorage.getItem(this.config.storageKey)
      if (stored) {
        this.logs = JSON.parse(stored)
      }
    } catch (e) {
      console.error('Failed to load logs from storage:', e)
    }
  }

  private saveLogs(): void {
    if (!this.config.enableStorage) return

    try {
      // Trim logs if they exceed max
      if (this.logs.length > this.config.maxStoredLogs) {
        this.logs = this.logs.slice(-this.config.maxStoredLogs)
      }

      localStorage.setItem(this.config.storageKey, JSON.stringify(this.logs))
    } catch (e) {
      console.error('Failed to save logs to storage:', e)
    }
  }

  private formatMessage(level: LogLevel, levelName: string, message: string, context?: Record<string, unknown>): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      levelName,
      message,
      context,
      sessionId: this.sessionId,
    }
  }

  private log(entry: LogEntry): void {
    // Filter by min level
    if (entry.level < this.config.minLevel) return

    // Add to logs array
    this.logs.push(entry)
    this.saveLogs()

    // Console output
    if (this.config.enableConsole) {
      this.logToConsole(entry)
    }
  }

  private logToConsole(entry: LogEntry): void {
    const prefix = `[${entry.timestamp}] [${entry.levelName}]`

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(prefix, entry.message, entry.context || '')
        break
      case LogLevel.INFO:
        console.info(prefix, entry.message, entry.context || '')
        break
      case LogLevel.WARNING:
        console.warn(prefix, entry.message, entry.context || '')
        break
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        console.error(prefix, entry.message, entry.context || '', entry.error || '')
        break
    }
  }

  /**
   * Log a debug message
   */
  debug(message: string, context?: Record<string, unknown>): void {
    const entry = this.formatMessage(LogLevel.DEBUG, 'DEBUG', message, context)
    this.log(entry)
  }

  /**
   * Log an info message
   */
  info(message: string, context?: Record<string, unknown>): void {
    const entry = this.formatMessage(LogLevel.INFO, 'INFO', message, context)
    this.log(entry)
  }

  /**
   * Log a warning message
   */
  warn(message: string, context?: Record<string, unknown>): void {
    const entry = this.formatMessage(LogLevel.WARNING, 'WARNING', message, context)
    this.log(entry)
  }

  /**
   * Log an error message
   */
  error(message: string, error?: Error, context?: Record<string, unknown>): void {
    const entry = this.formatMessage(LogLevel.ERROR, 'ERROR', message, context)

    if (error && this.config.enableStackTrace) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: error.stack,
      }
    }

    this.log(entry)
  }

  /**
   * Log a critical error
   */
  critical(message: string, error?: Error, context?: Record<string, unknown>): void {
    const entry = this.formatMessage(LogLevel.CRITICAL, 'CRITICAL', message, context)

    if (error && this.config.enableStackTrace) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: error.stack,
      }
    }

    this.log(entry)
  }

  /**
   * Log an API request
   */
  apiRequest(method: string, url: string, context?: Record<string, unknown>): void {
    this.info(`API ${method} ${url}`, {
      type: 'api_request',
      method,
      url,
      ...context,
    })
  }

  /**
   * Log an API response
   */
  apiResponse(method: string, url: string, status: number, durationMs: number): void {
    const level = status >= 400 ? LogLevel.WARNING : LogLevel.INFO
    const entry = this.formatMessage(level, status >= 400 ? 'WARNING' : 'INFO', `API ${method} ${url} - ${status}`, {
      type: 'api_response',
      method,
      url,
      status,
      durationMs,
    })
    this.log(entry)
  }

  /**
   * Log a user action
   */
  userAction(action: string, context?: Record<string, unknown>): void {
    this.info(`User action: ${action}`, {
      type: 'user_action',
      action,
      ...context,
    })
  }

  /**
   * Set the minimum log level
   */
  setMinLevel(level: LogLevel): void {
    this.config.minLevel = level
  }

  /**
   * Get all logs
   */
  getLogs(): LogEntry[] {
    return [...this.logs]
  }

  /**
   * Get logs filtered by level
   */
  getLogsByLevel(level: LogLevel): LogEntry[] {
    return this.logs.filter(log => log.level === level)
  }

  /**
   * Get logs filtered by type
   */
  getLogsByType(type: string): LogEntry[] {
    return this.logs.filter(log => log.context?.type === type)
  }

  /**
   * Clear all logs
   */
  clearLogs(): void {
    this.logs = []
    this.saveLogs()
  }

  /**
   * Export logs as JSON string
   */
  exportLogs(): string {
    return JSON.stringify({
      sessionId: this.sessionId,
      exportTime: new Date().toISOString(),
      logs: this.logs,
    }, null, 2)
  }

  /**
   * Download logs as a file
   */
  downloadLogs(): void {
    const data = this.exportLogs()
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rftip_logs_${new Date().toISOString().replace(/[:.]/g, '-')}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  /**
   * Get log statistics
   */
  getStats(): {
    total: number
    byLevel: Record<string, number>
    sessionDuration: number
  } {
    const byLevel: Record<string, number> = {}
    for (const log of this.logs) {
      byLevel[log.levelName] = (byLevel[log.levelName] || 0) + 1
    }

    const sessionStart = parseInt(this.sessionId.split('_')[1])
    const sessionDuration = Date.now() - sessionStart

    return {
      total: this.logs.length,
      byLevel,
      sessionDuration,
    }
  }
}

// Create singleton instance
const logger = new Logger({
  minLevel: import.meta.env.DEV ? LogLevel.DEBUG : LogLevel.WARNING,
  enableConsole: import.meta.env.DEV,
  enableStorage: true,
  maxStoredLogs: 500,
})

// Export logger instance and enum
export { logger }
export default logger

// Global error handlers
if (typeof window !== 'undefined') {
  // Handle unhandled errors
  window.addEventListener('error', (event) => {
    logger.critical(
      'Unhandled error',
      event.error,
      {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      }
    )
  })

  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    logger.critical(
      'Unhandled promise rejection',
      event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
      {
        type: 'promise_rejection',
      }
    )
  })

  // Log page visibility changes
  document.addEventListener('visibilitychange', () => {
    logger.info(`Page visibility changed to: ${document.visibilityState}`)
  })
}
