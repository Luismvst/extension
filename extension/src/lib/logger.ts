/**
 * Enhanced logging utility for the Chrome extension
 * Provides beautiful, structured console output for debugging
 */

export class Logger {
  private static colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    dim: '\x1b[2m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m',
    bgRed: '\x1b[41m',
    bgGreen: '\x1b[42m',
    bgYellow: '\x1b[43m',
    bgBlue: '\x1b[44m'
  }

  private static formatTimestamp(): string {
    return new Date().toISOString().substr(11, 12)
  }

  private static formatObject(obj: any, title: string = ''): string {
    const jsonStr = JSON.stringify(obj, null, 2)
    const lines = jsonStr.split('\n')
    const maxWidth = 80
    const border = '─'.repeat(maxWidth)
    
    let result = `\n${border}\n`
    if (title) {
      result += `📋 ${title}\n`
      result += `${border}\n`
    }
    
    lines.forEach(line => {
      result += `│ ${line.padEnd(maxWidth - 4)} │\n`
    })
    
    result += `${border}\n`
    return result
  }

  static info(message: string, data?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.cyan}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}ℹ️  ${message}${this.colors.reset}`
    )
    if (data) {
      console.log(this.formatObject(data, 'Data'))
    }
  }

  static success(message: string, data?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.green}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}✅ ${message}${this.colors.reset}`
    )
    if (data) {
      console.log(this.formatObject(data, 'Result'))
    }
  }

  static warning(message: string, data?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.yellow}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}⚠️  ${message}${this.colors.reset}`
    )
    if (data) {
      console.log(this.formatObject(data, 'Warning Data'))
    }
  }

  static error(message: string, error?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.red}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}❌ ${message}${this.colors.reset}`
    )
    if (error) {
      console.log(this.formatObject(error, 'Error Details'))
    }
  }

  static apiRequest(method: string, url: string, data?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.blue}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}🚀 API REQUEST${this.colors.reset}`
    )
    console.log(`${this.colors.cyan}Method:${this.colors.reset} ${method}`)
    console.log(`${this.colors.cyan}URL:${this.colors.reset} ${url}`)
    if (data) {
      console.log(this.formatObject(data, 'Request Payload'))
    }
  }

  static apiResponse(status: number, data?: any): void {
    const timestamp = this.formatTimestamp()
    const statusColor = status >= 200 && status < 300 ? this.colors.green : this.colors.red
    console.log(
      `${this.colors.blue}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}📡 API RESPONSE${this.colors.reset}`
    )
    console.log(`${this.colors.cyan}Status:${this.colors.reset} ${statusColor}${status}${this.colors.reset}`)
    if (data) {
      console.log(this.formatObject(data, 'Response Data'))
    }
  }

  static step(stepNumber: number, totalSteps: number, message: string, data?: any): void {
    const timestamp = this.formatTimestamp()
    console.log(
      `${this.colors.magenta}[${timestamp}]${this.colors.reset} ` +
      `${this.colors.bright}🔄 STEP ${stepNumber}/${totalSteps}: ${message}${this.colors.reset}`
    )
    if (data) {
      console.log(this.formatObject(data, 'Step Data'))
    }
  }

  static section(title: string): void {
    const border = '═'.repeat(60)
    console.log(`\n${this.colors.bright}${this.colors.blue}${border}`)
    console.log(`${this.colors.bright}${this.colors.blue}  ${title}`)
    console.log(`${this.colors.bright}${this.colors.blue}${border}${this.colors.reset}\n`)
  }
}

export default Logger
