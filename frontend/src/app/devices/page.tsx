'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { getDevices, createDevice, updateDevice, deleteDevice, Device, DeviceCreate } from '@/lib/api-client';
import { Plus, Edit, Trash2, Power, Clock, Star, Settings } from 'lucide-react';

const DEFAULT_MICROGRID_ID = 'microgrid_001';

function DevicesPageContent() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [formData, setFormData] = useState<DeviceCreate>({
    name: '',
    power_consumption_watts: 0,
    device_type: 'flexible',
    minimum_runtime_minutes: 0,
    priority_level: 3,
  });

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      setLoading(true);
      const data = await getDevices(DEFAULT_MICROGRID_ID);
      setDevices(data);
    } catch (error) {
      console.error('Failed to load devices:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingDevice) {
        await updateDevice(DEFAULT_MICROGRID_ID, editingDevice.id, formData);
      } else {
        await createDevice(DEFAULT_MICROGRID_ID, formData);
      }
      setShowModal(false);
      setEditingDevice(null);
      resetForm();
      loadDevices();
    } catch (error) {
      console.error('Failed to save device:', error);
      alert('Failed to save device. Please try again.');
    }
  };

  const handleEdit = (device: Device) => {
    setEditingDevice(device);
    setFormData({
      name: device.name,
      power_consumption_watts: device.power_consumption_watts,
      device_type: device.device_type,
      minimum_runtime_minutes: device.minimum_runtime_minutes,
      preferred_hours: device.preferred_hours,
      priority_level: device.priority_level,
    });
    setShowModal(true);
  };

  const handleDelete = async (deviceId: number) => {
    if (!confirm('Are you sure you want to delete this device?')) return;
    try {
      await deleteDevice(DEFAULT_MICROGRID_ID, deviceId);
      loadDevices();
    } catch (error) {
      console.error('Failed to delete device:', error);
      alert('Failed to delete device. Please try again.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      power_consumption_watts: 0,
      device_type: 'flexible',
      minimum_runtime_minutes: 0,
      priority_level: 3,
    });
  };

  const getDeviceTypeColor = (type: string) => {
    switch (type) {
      case 'essential':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'flexible':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'optional':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-50">Device Management</h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Manage your devices and their power consumption settings
            </p>
          </div>
          <button
            onClick={() => {
              setEditingDevice(null);
              resetForm();
              setShowModal(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Device
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device) => (
            <div
              key={device.id}
              className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50">{device.name}</h3>
                  <span className={`inline-block px-2 py-1 rounded text-xs font-medium mt-2 ${getDeviceTypeColor(device.device_type)}`}>
                    {device.device_type}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(device)}
                    className="p-2 text-slate-600 dark:text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(device.id)}
                    className="p-2 text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <Power className="w-4 h-4" />
                  <span>{(device.power_consumption_watts / 1000).toFixed(2)} kW</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <Clock className="w-4 h-4" />
                  <span>Min runtime: {device.minimum_runtime_minutes} min</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                  <Star className="w-4 h-4" />
                  <span>Priority: {device.priority_level}/5</span>
                </div>
                {device.preferred_hours && (
                  <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                    <Settings className="w-4 h-4" />
                    <span>
                      Preferred: {device.preferred_hours.start}:00 - {device.preferred_hours.end}:00
                    </span>
                  </div>
                )}
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <span
                    className={`text-xs font-medium ${
                      device.is_active
                        ? 'text-green-600 dark:text-green-400'
                        : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {device.is_active ? '● Active' : '○ Inactive'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {devices.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400 mb-4">No devices found. Add your first device to get started.</p>
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-slate-900 rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-50 mb-6">
                {editingDevice ? 'Edit Device' : 'Add New Device'}
              </h2>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Device Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Power Consumption (Watts)
                  </label>
                  <input
                    type="number"
                    required
                    min="1"
                    step="1"
                    value={formData.power_consumption_watts}
                    onChange={(e) => setFormData({ ...formData, power_consumption_watts: parseFloat(e.target.value) })}
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Device Type
                  </label>
                  <select
                    required
                    value={formData.device_type}
                    onChange={(e) => setFormData({ ...formData, device_type: e.target.value as any })}
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                  >
                    <option value="essential">Essential (Must run)</option>
                    <option value="flexible">Flexible (Can be scheduled)</option>
                    <option value="optional">Optional (Low priority)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Minimum Runtime (minutes)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={formData.minimum_runtime_minutes}
                    onChange={(e) => setFormData({ ...formData, minimum_runtime_minutes: parseInt(e.target.value) || 0 })}
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Priority Level (1-5, 1 is highest)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={formData.priority_level}
                    onChange={(e) => setFormData({ ...formData, priority_level: parseInt(e.target.value) || 3 })}
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Preferred Start Hour (0-23)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={formData.preferred_hours?.start || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          preferred_hours: {
                            start: parseInt(e.target.value) || 0,
                            end: formData.preferred_hours?.end || 23,
                          },
                        })
                      }
                      className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                      Preferred End Hour (0-23)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="23"
                      value={formData.preferred_hours?.end || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          preferred_hours: {
                            start: formData.preferred_hours?.start || 0,
                            end: parseInt(e.target.value) || 23,
                          },
                        })
                      }
                      className="w-full px-4 py-2 border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50"
                    />
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
                  >
                    {editingDevice ? 'Update Device' : 'Create Device'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowModal(false);
                      setEditingDevice(null);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-50 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DevicesPage() {
  return (
    <ProtectedRoute>
      <DevicesPageContent />
    </ProtectedRoute>
  );
}

