import { describe, it, expect, beforeEach, vi } from 'vitest'
import { FrontLogger } from '@/lib/frontLogger'

// Mock Chrome storage
const mockStorage = {
  get: vi.fn(),
  set: vi.fn(),
  remove: vi.fn(),
  clear: vi.fn()
}

vi.mock('chrome', () => ({
  storage: {
    local: mockStorage
  }
}))

describe('FrontLogger', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockStorage.get.mockResolvedValue({ frontLogs: [] })
    mockStorage.set.mockResolvedValue(undefined)
  })

  it('should push log entry', async () => {
    const logger = new FrontLogger()
    await logger.push('TEST_ACTION', true, 'Test message', { test: 'data' })

    expect(mockStorage.get).toHaveBeenCalledWith('frontLogs')
    expect(mockStorage.set).toHaveBeenCalled()
  })

  it('should get all logs', async () => {
    const mockLogs = [
      {
        ts: '2024-01-01T00:00:00.000Z',
        action: 'TEST_ACTION',
        ok: true,
        msg: 'Test message',
        details: { test: 'data' }
      }
    ]

    mockStorage.get.mockResolvedValue({ frontLogs: mockLogs })

    const logger = new FrontLogger()
    const logs = await logger.getAll()

    expect(logs).toEqual(mockLogs)
  })

  it('should clear logs', async () => {
    const logger = new FrontLogger()
    await logger.clear()

    expect(mockStorage.set).toHaveBeenCalledWith({ frontLogs: [] })
  })

  it('should export CSV', async () => {
    const mockLogs = [
      {
        ts: '2024-01-01T00:00:00.000Z',
        action: 'TEST_ACTION',
        ok: true,
        msg: 'Test message',
        details: { test: 'data' }
      }
    ]

    mockStorage.get.mockResolvedValue({ frontLogs: mockLogs })

    const logger = new FrontLogger()
    const csv = await logger.exportCSV()

    expect(csv).toContain('ts;action;ok;msg;details_json')
    expect(csv).toContain('TEST_ACTION')
  })

  it('should rotate logs when exceeding max entries', async () => {
    const mockLogs = Array(2001).fill({
      ts: '2024-01-01T00:00:00.000Z',
      action: 'TEST_ACTION',
      ok: true,
      msg: 'Test message',
      details: {}
    })

    mockStorage.get.mockResolvedValue({ frontLogs: mockLogs })

    const logger = new FrontLogger()
    await logger.push('NEW_ACTION', true, 'New message', {})

    expect(mockStorage.set).toHaveBeenCalledWith({
      frontLogs: expect.arrayContaining([
        expect.objectContaining({ action: 'NEW_ACTION' })
      ])
    })

    // Should have removed old entries to stay under 2000
    const setCall = mockStorage.set.mock.calls[0]
    const logs = setCall[0].frontLogs
    expect(logs.length).toBeLessThanOrEqual(2000)
  })
})
