import React, { useState, useEffect } from 'react'
import { OrderStandard } from '@/common/types'
import { getQueue, clearQueue, generateTIPSA } from '@/common/messages'
import { exportTIPSACSV } from '@/mappers/tipsa'
import { Download, Trash2, RefreshCw, FileText, Package } from 'lucide-react'

/**
 * Main popup component for the Mirakl CSV Extension
 */
export default function App() {
  const [orders, setOrders] = useState<OrderStandard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState({
    total: 0,
    byStatus: {
      PENDING: 0,
      ACCEPTED: 0,
      SHIPPED: 0,
      DELIVERED: 0,
      CANCELLED: 0
    }
  })

  useEffect(() => {
    loadOrders()
  }, [])

  /**
   * Load orders from background script
   */
  const loadOrders = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await getQueue()
      setOrders(response.orders || [])
      setStats(response.stats || {
        total: 0,
        byStatus: {
          PENDING: 0,
          ACCEPTED: 0,
          SHIPPED: 0,
          DELIVERED: 0,
          CANCELLED: 0
        }
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load orders')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Clear all orders
   */
  const handleClearOrders = async () => {
    try {
      await clearQueue()
      setOrders([])
      setStats({
        total: 0,
        byStatus: {
          PENDING: 0,
          ACCEPTED: 0,
          SHIPPED: 0,
          DELIVERED: 0,
          CANCELLED: 0
        }
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear orders')
    }
  }

  /**
   * Generate and download TIPSA CSV
   */
  const handleGenerateTIPSA = async () => {
    try {
      if (orders.length === 0) {
        setError('No orders to export')
        return
      }

      const filename = `tipsa_orders_${new Date().toISOString().split('T')[0]}.csv`
      exportTIPSACSV(orders, filename)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate TIPSA CSV')
    }
  }

  /**
   * Get status color
   */
  const getStatusColor = (status: OrderStandard['status']) => {
    const colors = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      ACCEPTED: 'bg-blue-100 text-blue-800',
      SHIPPED: 'bg-purple-100 text-purple-800',
      DELIVERED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  /**
   * Format date
   */
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  /**
   * Format currency
   */
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="w-96 p-4">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-500" />
          <span className="ml-2 text-gray-600">Loading orders...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="w-96 p-4 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-lg font-semibold text-gray-900">
          Mirakl CSV Extension
        </h1>
        <button
          onClick={loadOrders}
          className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
          <div className="text-sm text-blue-600">Total Orders</div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{stats.byStatus.PENDING}</div>
          <div className="text-sm text-green-600">Pending</div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <div className="text-red-800 text-sm">{error}</div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={handleGenerateTIPSA}
          disabled={orders.length === 0}
          className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
        >
          <Download className="w-4 h-4 mr-2" />
          Generate TIPSA CSV
        </button>
        <button
          onClick={handleClearOrders}
          disabled={orders.length === 0}
          className="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Orders List */}
      {orders.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Package className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>No orders found</p>
          <p className="text-sm">Export CSV from a Mirakl marketplace to get started</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {orders.map((order) => (
            <div key={order.orderId} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{order.orderId}</div>
                  <div className="text-sm text-gray-500">{formatDate(order.createdAt)}</div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                  {order.status}
                </span>
              </div>
              
              <div className="text-sm text-gray-600 mb-2">
                <div>{order.buyer.name}</div>
                <div>{order.shipping.city}, {order.shipping.postcode}</div>
              </div>
              
              <div className="flex items-center justify-between text-sm">
                <div className="text-gray-500">
                  {order.items.length} item{order.items.length !== 1 ? 's' : ''}
                </div>
                <div className="font-medium text-gray-900">
                  {formatCurrency(order.totals.goods)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-center text-xs text-gray-500">
        <div>Mirakl CSV Extension v0.1.0</div>
        <div>Ready for TIPSA integration</div>
      </div>
    </div>
  )
}
