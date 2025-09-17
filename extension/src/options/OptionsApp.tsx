import React, { useState, useEffect } from 'react'
import { StorageManager } from '@/lib/storage'
import { Settings, Save, RefreshCw, Trash2, Download, Upload } from 'lucide-react'

interface ExtensionSettings {
  autoExport: boolean
  defaultService: string
  cleanupDays: number
  notifications: boolean
  backupEnabled: boolean
  debugMode: boolean
}

const defaultSettings: ExtensionSettings = {
  autoExport: false,
  defaultService: 'ESTANDAR',
  cleanupDays: 7,
  notifications: true,
  backupEnabled: true,
  debugMode: false
}

export default function OptionsApp() {
  const [settings, setSettings] = useState<ExtensionSettings>(defaultSettings)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const savedSettings = await StorageManager.getSettings()
      setSettings({ ...defaultSettings, ...savedSettings })
    } catch (error) {
      console.error('Failed to load settings:', error)
      setMessage({ type: 'error', text: 'Failed to load settings' })
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    try {
      setSaving(true)
      setMessage(null)
      
      await StorageManager.setSettings(settings)
      setMessage({ type: 'success', text: 'Settings saved successfully' })
    } catch (error) {
      console.error('Failed to save settings:', error)
      setMessage({ type: 'error', text: 'Failed to save settings' })
    } finally {
      setSaving(false)
    }
  }

  const resetSettings = async () => {
    try {
      setSettings(defaultSettings)
      await StorageManager.setSettings(defaultSettings)
      setMessage({ type: 'success', text: 'Settings reset to defaults' })
    } catch (error) {
      console.error('Failed to reset settings:', error)
      setMessage({ type: 'error', text: 'Failed to reset settings' })
    }
  }

  const exportData = async () => {
    try {
      const orders = await StorageManager.getOrdersQueue()
      const settings = await StorageManager.getSettings()
      
      const exportData = {
        orders,
        settings,
        exportDate: new Date().toISOString(),
        version: '0.1.0'
      }
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `mirakl-extension-backup-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      setMessage({ type: 'success', text: 'Data exported successfully' })
    } catch (error) {
      console.error('Failed to export data:', error)
      setMessage({ type: 'error', text: 'Failed to export data' })
    }
  }

  const importData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target?.result as string)
        
        if (data.orders) {
          await StorageManager.setOrdersQueue(data.orders)
        }
        
        if (data.settings) {
          await StorageManager.setSettings(data.settings)
          setSettings({ ...defaultSettings, ...data.settings })
        }
        
        setMessage({ type: 'success', text: 'Data imported successfully' })
      } catch (error) {
        console.error('Failed to import data:', error)
        setMessage({ type: 'error', text: 'Failed to import data' })
      }
    }
    reader.readAsText(file)
  }

  const clearAllData = async () => {
    if (!confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
      return
    }

    try {
      await StorageManager.clear()
      setSettings(defaultSettings)
      setMessage({ type: 'success', text: 'All data cleared successfully' })
    } catch (error) {
      console.error('Failed to clear data:', error)
      setMessage({ type: 'error', text: 'Failed to clear data' })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Settings className="w-6 h-6 mr-3 text-blue-500" />
              Mirakl CSV Extension Settings
            </h1>
            <p className="text-gray-600 mt-1">Configure your extension preferences</p>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {message.text}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Settings Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">General Settings</h2>
              </div>
              <div className="px-6 py-4 space-y-6">
                {/* Auto Export */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Auto Export</label>
                    <p className="text-sm text-gray-500">Automatically export CSV when detected</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.autoExport}
                      onChange={(e) => setSettings({ ...settings, autoExport: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* Default Service */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Default TIPSA Service</label>
                  <select
                    value={settings.defaultService}
                    onChange={(e) => setSettings({ ...settings, defaultService: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="ESTANDAR">Estándar</option>
                    <option value="URGENTE">Urgente</option>
                    <option value="EXPRESS">Express</option>
                    <option value="ECONOMICO">Económico</option>
                  </select>
                </div>

                {/* Cleanup Days */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cleanup Days</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={settings.cleanupDays}
                    onChange={(e) => setSettings({ ...settings, cleanupDays: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-sm text-gray-500 mt-1">Remove orders older than this many days</p>
                </div>

                {/* Notifications */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Notifications</label>
                    <p className="text-sm text-gray-500">Show success/error notifications</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.notifications}
                      onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {/* Debug Mode */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Debug Mode</label>
                    <p className="text-sm text-gray-500">Enable detailed logging</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.debugMode}
                      onChange={(e) => setSettings({ ...settings, debugMode: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Actions Sidebar */}
          <div className="space-y-6">
            {/* Save Settings */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Actions</h3>
              </div>
              <div className="px-6 py-4 space-y-3">
                <button
                  onClick={saveSettings}
                  disabled={saving}
                  className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  {saving ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Save className="w-4 h-4 mr-2" />
                  )}
                  {saving ? 'Saving...' : 'Save Settings'}
                </button>

                <button
                  onClick={resetSettings}
                  className="w-full bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Reset to Defaults
                </button>
              </div>
            </div>

            {/* Data Management */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Data Management</h3>
              </div>
              <div className="px-6 py-4 space-y-3">
                <button
                  onClick={exportData}
                  className="w-full bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </button>

                <label className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center cursor-pointer">
                  <Upload className="w-4 h-4 mr-2" />
                  Import Data
                  <input
                    type="file"
                    accept=".json"
                    onChange={importData}
                    className="hidden"
                  />
                </label>

                <button
                  onClick={clearAllData}
                  className="w-full bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center justify-center"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear All Data
                </button>
              </div>
            </div>

            {/* Extension Info */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Extension Info</h3>
              </div>
              <div className="px-6 py-4 text-sm text-gray-600">
                <div className="space-y-2">
                  <div><strong>Version:</strong> 0.1.0</div>
                  <div><strong>Status:</strong> Active</div>
                  <div><strong>Last Updated:</strong> {new Date().toLocaleDateString()}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
