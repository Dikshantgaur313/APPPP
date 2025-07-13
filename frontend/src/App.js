import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [detectors, setDetectors] = useState([]);
  const [extinguishers, setExtinguishers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [dashboardData, setDashboardData] = useState({
    detectors: { total: 0, active: 0, triggered: 0 },
    extinguishers: { total: 0, triggered: 0 },
    recent_alerts: []
  });
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [showAddDetector, setShowAddDetector] = useState(false);
  const [showAddExtinguisher, setShowAddExtinguisher] = useState(false);
  const [showEditDetector, setShowEditDetector] = useState(false);
  const [showEditExtinguisher, setShowEditExtinguisher] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [newDetector, setNewDetector] = useState({ name: "", location: "", battery_level: 100 });
  const [newExtinguisher, setNewExtinguisher] = useState({ 
    name: "", 
    location: "", 
    last_refill: "", 
    last_pressure_test: "" 
  });

  // Load data functions
  const loadDetectors = async () => {
    try {
      const response = await axios.get(`${API}/smoke-detectors`);
      setDetectors(response.data);
    } catch (error) {
      console.error("Error loading detectors:", error);
    }
  };

  const loadExtinguishers = async () => {
    try {
      const response = await axios.get(`${API}/fire-extinguishers`);
      setExtinguishers(response.data);
    } catch (error) {
      console.error("Error loading extinguishers:", error);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await axios.get(`${API}/alerts`);
      setAlerts(response.data);
    } catch (error) {
      console.error("Error loading alerts:", error);
    }
  };

  const loadDashboard = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error("Error loading dashboard:", error);
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadDetectors(), loadExtinguishers(), loadAlerts(), loadDashboard()]);
      setLoading(false);
    };
    loadData();

    // Set up polling for real-time updates
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Admin functions
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/admin/login`, loginData);
      if (response.data.admin) {
        setIsAdmin(true);
        setShowLogin(false);
        setLoginData({ username: "", password: "" });
      }
    } catch (error) {
      alert("Invalid admin credentials");
    }
  };

  const handleLogout = () => {
    setIsAdmin(false);
    setShowLogin(false);
  };

  const handleAddDetector = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/smoke-detectors`, newDetector, {
        auth: { username: "admin", password: "firesafety2025" }
      });
      setNewDetector({ name: "", location: "", battery_level: 100 });
      setShowAddDetector(false);
      await loadDetectors();
      await loadDashboard();
    } catch (error) {
      alert("Error adding detector");
    }
  };

  const handleAddExtinguisher = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/fire-extinguishers`, newExtinguisher, {
        auth: { username: "admin", password: "firesafety2025" }
      });
      setNewExtinguisher({ name: "", location: "", last_refill: "", last_pressure_test: "" });
      setShowAddExtinguisher(false);
      await loadExtinguishers();
      await loadDashboard();
    } catch (error) {
      alert("Error adding extinguisher");
    }
  };

  const handleEditDetector = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/admin/smoke-detectors/${editingItem.id}`, {
        name: editingItem.name,
        location: editingItem.location,
        battery_level: editingItem.battery_level
      }, {
        auth: { username: "admin", password: "firesafety2025" }
      });
      setShowEditDetector(false);
      setEditingItem(null);
      await loadDetectors();
    } catch (error) {
      alert("Error updating detector");
    }
  };

  const handleEditExtinguisher = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/admin/fire-extinguishers/${editingItem.id}`, {
        name: editingItem.name,
        location: editingItem.location,
        last_refill: editingItem.last_refill,
        last_pressure_test: editingItem.last_pressure_test
      }, {
        auth: { username: "admin", password: "firesafety2025" }
      });
      setShowEditExtinguisher(false);
      setEditingItem(null);
      await loadExtinguishers();
    } catch (error) {
      alert("Error updating extinguisher");
    }
  };

  const handleDeleteDetector = async (id) => {
    if (window.confirm("Are you sure you want to delete this detector?")) {
      try {
        await axios.delete(`${API}/admin/smoke-detectors/${id}`, {
          auth: { username: "admin", password: "firesafety2025" }
        });
        await loadDetectors();
        await loadDashboard();
      } catch (error) {
        alert("Error deleting detector");
      }
    }
  };

  const handleDeleteExtinguisher = async (id) => {
    if (window.confirm("Are you sure you want to delete this extinguisher?")) {
      try {
        await axios.delete(`${API}/admin/fire-extinguishers/${id}`, {
          auth: { username: "admin", password: "firesafety2025" }
        });
        await loadExtinguishers();
        await loadDashboard();
      } catch (error) {
        alert("Error deleting extinguisher");
      }
    }
  };

  // Action functions
  const triggerDetector = async (detectorId) => {
    try {
      await axios.post(`${API}/smoke-detectors/${detectorId}/trigger`);
      await loadDetectors();
      await loadAlerts();
      await loadDashboard();
    } catch (error) {
      console.error("Error triggering detector:", error);
    }
  };

  const resetDetector = async (detectorId) => {
    try {
      await axios.post(`${API}/smoke-detectors/${detectorId}/reset`);
      await loadDetectors();
      await loadDashboard();
    } catch (error) {
      console.error("Error resetting detector:", error);
    }
  };

  const triggerExtinguisher = async (extinguisherId) => {
    try {
      await axios.post(`${API}/fire-extinguishers/${extinguisherId}/trigger`);
      await loadExtinguishers();
      await loadAlerts();
      await loadDashboard();
    } catch (error) {
      console.error("Error triggering extinguisher:", error);
    }
  };

  const refillExtinguisher = async (extinguisherId) => {
    try {
      await axios.post(`${API}/fire-extinguishers/${extinguisherId}/refill`);
      await loadExtinguishers();
      await loadDashboard();
    } catch (error) {
      console.error("Error refilling extinguisher:", error);
      alert("Error refilling extinguisher. May not be due for refill.");
    }
  };

  const testExtinguisher = async (extinguisherId) => {
    try {
      await axios.post(`${API}/fire-extinguishers/${extinguisherId}/pressure-test`);
      await loadExtinguishers();
      await loadDashboard();
    } catch (error) {
      console.error("Error testing extinguisher:", error);
      alert("Error testing extinguisher. May not be due for pressure test.");
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await axios.put(`${API}/alerts/${alertId}/acknowledge`);
      await loadAlerts();
      await loadDashboard();
    } catch (error) {
      console.error("Error acknowledging alert:", error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDaysUntil = (dateString) => {
    const targetDate = new Date(dateString);
    const today = new Date();
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "bg-green-500";
      case "triggered":
        return "bg-red-500";
      case "refill_due":
        return "bg-yellow-500";
      case "pressure_test_due":
        return "bg-orange-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "active":
        return "Active";
      case "triggered":
        return "TRIGGERED";
      case "refill_due":
        return "Refill Due";
      case "pressure_test_due":
        return "Pressure Test Due";
      default:
        return status;
    }
  };

  const isExtinguisherDue = (extinguisher) => {
    const now = new Date();
    const refillDue = new Date(extinguisher.next_refill_due);
    const pressureTestDue = new Date(extinguisher.next_pressure_test_due);
    const refillDays = Math.ceil((refillDue - now) / (1000 * 60 * 60 * 24));
    const pressureTestDays = Math.ceil((pressureTestDue - now) / (1000 * 60 * 60 * 24));
    
    return {
      refillDue: refillDays <= 30 || extinguisher.status === "triggered",
      pressureTestDue: pressureTestDays <= 30
    };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading APEX FIRE Protection System...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-red-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-3xl font-bold">APEX FIRE</div>
              <div>
                <h1 className="text-2xl font-bold">APEX FIRE PROTECTION SYSTEM</h1>
                <p className="text-red-100">Real-time monitoring and alerts</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm">
                <div>Active Detectors: {dashboardData.detectors.active}</div>
                <div>Triggered: {dashboardData.detectors.triggered}</div>
              </div>
              {isAdmin ? (
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-800 text-white rounded hover:bg-red-900"
                >
                  Logout Admin
                </button>
              ) : (
                <button
                  onClick={() => setShowLogin(true)}
                  className="px-4 py-2 bg-red-800 text-white rounded hover:bg-red-900"
                >
                  Admin Login
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-8">
            {["dashboard", "detectors", "extinguishers", "alerts"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? "border-red-500 text-red-400"
                    : "border-transparent text-gray-300 hover:text-white hover:border-gray-300"
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Login Modal */}
      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Admin Login</h2>
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Username</label>
                <input
                  type="text"
                  value={loginData.username}
                  onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Password</label>
                <input
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowLogin(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                >
                  Login
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Detector Modal */}
      {showAddDetector && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Add Smoke Detector</h2>
            <form onSubmit={handleAddDetector}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={newDetector.name}
                  onChange={(e) => setNewDetector({...newDetector, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Location</label>
                <input
                  type="text"
                  value={newDetector.location}
                  onChange={(e) => setNewDetector({...newDetector, location: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Battery Level (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={newDetector.battery_level}
                  onChange={(e) => setNewDetector({...newDetector, battery_level: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddDetector(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Detector
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Extinguisher Modal */}
      {showAddExtinguisher && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Add Fire Extinguisher</h2>
            <form onSubmit={handleAddExtinguisher}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={newExtinguisher.name}
                  onChange={(e) => setNewExtinguisher({...newExtinguisher, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Location</label>
                <input
                  type="text"
                  value={newExtinguisher.location}
                  onChange={(e) => setNewExtinguisher({...newExtinguisher, location: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Last Refill Date</label>
                <input
                  type="date"
                  value={newExtinguisher.last_refill}
                  onChange={(e) => setNewExtinguisher({...newExtinguisher, last_refill: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Last Pressure Test Date</label>
                <input
                  type="date"
                  value={newExtinguisher.last_pressure_test}
                  onChange={(e) => setNewExtinguisher({...newExtinguisher, last_pressure_test: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddExtinguisher(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Extinguisher
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Detector Modal */}
      {showEditDetector && editingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Edit Smoke Detector</h2>
            <form onSubmit={handleEditDetector}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={editingItem.name}
                  onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Location</label>
                <input
                  type="text"
                  value={editingItem.location}
                  onChange={(e) => setEditingItem({...editingItem, location: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Battery Level (%)</label>
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={editingItem.battery_level}
                  onChange={(e) => setEditingItem({...editingItem, battery_level: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditDetector(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Update Detector
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Extinguisher Modal */}
      {showEditExtinguisher && editingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Edit Fire Extinguisher</h2>
            <form onSubmit={handleEditExtinguisher}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={editingItem.name}
                  onChange={(e) => setEditingItem({...editingItem, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Location</label>
                <input
                  type="text"
                  value={editingItem.location}
                  onChange={(e) => setEditingItem({...editingItem, location: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Last Refill Date</label>
                <input
                  type="date"
                  value={editingItem.last_refill ? editingItem.last_refill.split('T')[0] : ''}
                  onChange={(e) => setEditingItem({...editingItem, last_refill: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Last Pressure Test Date</label>
                <input
                  type="date"
                  value={editingItem.last_pressure_test ? editingItem.last_pressure_test.split('T')[0] : ''}
                  onChange={(e) => setEditingItem({...editingItem, last_pressure_test: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditExtinguisher(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Update Extinguisher
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Total Detectors</p>
                    <p className="text-3xl font-bold">{dashboardData.detectors.total}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">SD</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Active Detectors</p>
                    <p className="text-3xl font-bold text-green-400">{dashboardData.detectors.active}</p>
                  </div>
                  <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">OK</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Triggered Detectors</p>
                    <p className="text-3xl font-bold text-red-400">{dashboardData.detectors.triggered}</p>
                  </div>
                  <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">!</span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Triggered Extinguishers</p>
                    <p className="text-3xl font-bold text-red-400">{dashboardData.extinguishers.triggered}</p>
                  </div>
                  <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">FE</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
              {dashboardData.recent_alerts.length === 0 ? (
                <p className="text-gray-400">No recent alerts</p>
              ) : (
                <div className="space-y-3">
                  {dashboardData.recent_alerts.map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 bg-red-900 rounded-lg">
                      <div>
                        <p className="font-medium text-red-100">{alert.message}</p>
                        <p className="text-sm text-red-300">{formatDate(alert.timestamp)}</p>
                      </div>
                      <button
                        onClick={() => acknowledgeAlert(alert.id)}
                        className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Acknowledge
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "detectors" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Smoke Detectors</h2>
              {isAdmin && (
                <button
                  onClick={() => setShowAddDetector(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Detector
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {detectors.map((detector) => (
                <div key={detector.id} className="bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{detector.name}</h3>
                      <p className="text-gray-400">{detector.location}</p>
                    </div>
                    <div className={`w-4 h-4 rounded-full ${getStatusColor(detector.status)}`}></div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Status:</span>
                      <span className={`font-medium ${detector.status === "triggered" ? "text-red-400" : "text-green-400"}`}>
                        {getStatusText(detector.status)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Battery:</span>
                      <span>{detector.battery_level}%</span>
                    </div>
                    {detector.last_triggered && (
                      <div className="flex justify-between text-sm">
                        <span>Last Triggered:</span>
                        <span>{formatDate(detector.last_triggered)}</span>
                      </div>
                    )}
                  </div>
                  <div className="mt-4 flex space-x-2">
                    <button
                      onClick={() => triggerDetector(detector.id)}
                      className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Trigger
                    </button>
                    <button
                      onClick={() => resetDetector(detector.id)}
                      className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                    >
                      Reset
                    </button>
                  </div>
                  {isAdmin && (
                    <div className="mt-2 flex space-x-2">
                      <button
                        onClick={() => {
                          setEditingItem(detector);
                          setShowEditDetector(true);
                        }}
                        className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteDetector(detector.id)}
                        className="flex-1 px-3 py-2 bg-red-800 text-white rounded hover:bg-red-900"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "extinguishers" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Fire Extinguishers</h2>
              {isAdmin && (
                <button
                  onClick={() => setShowAddExtinguisher(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Extinguisher
                </button>
              )}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {extinguishers.map((extinguisher) => {
                const dueStatus = isExtinguisherDue(extinguisher);
                return (
                  <div key={extinguisher.id} className="bg-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold">{extinguisher.name}</h3>
                        <p className="text-gray-400">{extinguisher.location}</p>
                      </div>
                      <div className={`w-4 h-4 rounded-full ${getStatusColor(extinguisher.status)}`}></div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Status:</span>
                        <span className={`font-medium ${extinguisher.status === "active" ? "text-green-400" : "text-yellow-400"}`}>
                          {getStatusText(extinguisher.status)}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Last Refill:</span>
                        <span>{formatDate(extinguisher.last_refill)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Next Refill Due:</span>
                        <span className={getDaysUntil(extinguisher.next_refill_due) <= 30 ? "text-red-400" : ""}>
                          {formatDate(extinguisher.next_refill_due)}
                          <span className="text-gray-400"> ({getDaysUntil(extinguisher.next_refill_due)} days)</span>
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Last Pressure Test:</span>
                        <span>{formatDate(extinguisher.last_pressure_test)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Next Pressure Test:</span>
                        <span className={getDaysUntil(extinguisher.next_pressure_test_due) <= 30 ? "text-red-400" : ""}>
                          {formatDate(extinguisher.next_pressure_test_due)}
                          <span className="text-gray-400"> ({getDaysUntil(extinguisher.next_pressure_test_due)} days)</span>
                        </span>
                      </div>
                      {extinguisher.last_triggered && (
                        <div className="flex justify-between text-sm">
                          <span>Last Triggered:</span>
                          <span>{formatDate(extinguisher.last_triggered)}</span>
                        </div>
                      )}
                    </div>
                    <div className="mt-4 flex space-x-2">
                      <button
                        onClick={() => triggerExtinguisher(extinguisher.id)}
                        className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Trigger
                      </button>
                    </div>
                    {(dueStatus.refillDue || dueStatus.pressureTestDue) && (
                      <div className="mt-2 flex space-x-2">
                        {dueStatus.refillDue && (
                          <button
                            onClick={() => refillExtinguisher(extinguisher.id)}
                            className="flex-1 px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                          >
                            Refill
                          </button>
                        )}
                        {dueStatus.pressureTestDue && (
                          <button
                            onClick={() => testExtinguisher(extinguisher.id)}
                            className="flex-1 px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
                          >
                            Test
                          </button>
                        )}
                      </div>
                    )}
                    {isAdmin && (
                      <div className="mt-2 flex space-x-2">
                        <button
                          onClick={() => {
                            setEditingItem(extinguisher);
                            setShowEditExtinguisher(true);
                          }}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteExtinguisher(extinguisher.id)}
                          className="flex-1 px-3 py-2 bg-red-800 text-white rounded hover:bg-red-900"
                        >
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {activeTab === "alerts" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Alert History</h2>
            </div>
            <div className="bg-gray-800 rounded-lg overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Message</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {alerts.map((alert) => (
                      <tr key={alert.id} className={`${alert.acknowledged ? "bg-gray-800" : "bg-red-900"}`}>
                        <td className="px-6 py-4 text-sm">{formatDate(alert.timestamp)}</td>
                        <td className="px-6 py-4 text-sm">{alert.detector_location || alert.extinguisher_location}</td>
                        <td className="px-6 py-4 text-sm">{alert.message}</td>
                        <td className="px-6 py-4 text-sm">
                          {alert.acknowledged ? (
                            <span className="px-2 py-1 text-xs bg-green-600 text-white rounded">Acknowledged</span>
                          ) : (
                            <button
                              onClick={() => acknowledgeAlert(alert.id)}
                              className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                            >
                              Acknowledge
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;