import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [extinguisherSubTab, setExtinguisherSubTab] = useState("extinguishers");
  const [detectors, setDetectors] = useState([]);
  const [extinguishers, setExtinguishers] = useState([]);
  const [dispatchedExtinguishers, setDispatchedExtinguishers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [maintenanceItems, setMaintenanceItems] = useState([]);
  const [dashboardData, setDashboardData] = useState({
    detectors: { total: 0, active: 0, triggered: 0 },
    extinguishers: { total: 0, triggered: 0 },
    maintenance: { total: 0, pending: 0, overdue: 0 },
    recent_alerts: []
  });
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [resetData, setResetData] = useState({ reset_code: "", new_password: "" });
  const [showAddDetector, setShowAddDetector] = useState(false);
  const [showAddExtinguisher, setShowAddExtinguisher] = useState(false);
  const [showAddMaintenance, setShowAddMaintenance] = useState(false);
  const [showEditDetector, setShowEditDetector] = useState(false);
  const [showEditExtinguisher, setShowEditExtinguisher] = useState(false);
  const [showEditMaintenance, setShowEditMaintenance] = useState(false);
  const [showAddNote, setShowAddNote] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [selectedMaintenanceItem, setSelectedMaintenanceItem] = useState(null);
  const [newNote, setNewNote] = useState("");
  const [newDetector, setNewDetector] = useState({ name: "", location: "", battery_level: 100 });
  const [newExtinguisher, setNewExtinguisher] = useState({ 
    name: "", 
    location: "", 
    last_refill: "", 
    last_pressure_test: "" 
  });
  const [newMaintenanceItem, setNewMaintenanceItem] = useState({
    name: "",
    description: "",
    priority: "medium",
    assigned_to: "",
    due_date: ""
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

  const loadMaintenanceItems = async () => {
    try {
      const response = await axios.get(`${API}/maintenance-items`);
      setMaintenanceItems(response.data);
    } catch (error) {
      console.error("Error loading maintenance items:", error);
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

  const loadDispatchedExtinguishers = async () => {
    try {
      const response = await axios.get(`${API}/fire-extinguishers/dispatched`);
      setDispatchedExtinguishers(response.data);
    } catch (error) {
      console.error("Error loading dispatched extinguishers:", error);
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadDetectors(), loadExtinguishers(), loadAlerts(), loadMaintenanceItems(), loadDashboard(), loadDispatchedExtinguishers()]);
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

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/admin/reset-password`, resetData);
      alert("Password reset successfully!");
      setShowForgotPassword(false);
      setResetData({ reset_code: "", new_password: "" });
    } catch (error) {
      alert("Invalid reset code");
    }
  };

  const getResetCode = async () => {
    try {
      const response = await axios.get(`${API}/admin/reset-code`);
      alert(`Reset Code: ${response.data.reset_code}\n\nUse this code to reset your password.`);
    } catch (error) {
      alert("Error getting reset code");
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

  const handleAddMaintenanceItem = async (e) => {
    e.preventDefault();
    try {
      const itemToCreate = {
        ...newMaintenanceItem,
        due_date: newMaintenanceItem.due_date ? new Date(newMaintenanceItem.due_date).toISOString() : null
      };
      await axios.post(`${API}/maintenance-items`, itemToCreate);
      setNewMaintenanceItem({ name: "", description: "", priority: "medium", assigned_to: "", due_date: "" });
      setShowAddMaintenance(false);
      await loadMaintenanceItems();
      await loadDashboard();
    } catch (error) {
      alert("Error adding maintenance item");
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

  const handleEditMaintenanceItem = async (e) => {
    e.preventDefault();
    try {
      const itemToUpdate = {
        name: editingItem.name,
        description: editingItem.description,
        priority: editingItem.priority,
        assigned_to: editingItem.assigned_to,
        status: editingItem.status,
        due_date: editingItem.due_date ? new Date(editingItem.due_date).toISOString() : null
      };
      await axios.put(`${API}/maintenance-items/${editingItem.id}`, itemToUpdate);
      setShowEditMaintenance(false);
      setEditingItem(null);
      await loadMaintenanceItems();
      await loadDashboard();
    } catch (error) {
      alert("Error updating maintenance item");
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

  const handleDeleteMaintenanceItem = async (id) => {
    if (window.confirm("Are you sure you want to delete this maintenance item?")) {
      try {
        await axios.delete(`${API}/maintenance-items/${id}`);
        await loadMaintenanceItems();
        await loadDashboard();
      } catch (error) {
        alert("Error deleting maintenance item");
      }
    }
  };

  const handleAddNote = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/maintenance-items/${selectedMaintenanceItem.id}/notes`, {
        note: newNote
      });
      setNewNote("");
      setShowAddNote(false);
      await loadMaintenanceItems();
    } catch (error) {
      alert("Error adding note");
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

  // Dispatch functions
  const dispatchExtinguisher = async (id) => {
    try {
      await axios.post(`${API}/fire-extinguishers/${id}/dispatch`);
      await loadExtinguishers();
      await loadDispatchedExtinguishers();
      await loadDashboard();
    } catch (error) {
      console.error("Error dispatching extinguisher:", error);
      alert("Error dispatching extinguisher");
    }
  };

  const receiveExtinguisher = async (id) => {
    try {
      await axios.post(`${API}/fire-extinguishers/${id}/receive`);
      await loadExtinguishers();
      await loadDispatchedExtinguishers();
      await loadDashboard();
    } catch (error) {
      console.error("Error receiving extinguisher:", error);
      alert("Error receiving extinguisher");
    }
  };

  const updateDispatchStatus = async (id, status) => {
    try {
      await axios.put(`${API}/fire-extinguishers/${id}/dispatch-status`, status, {
        headers: { 'Content-Type': 'application/json' }
      });
      await loadDispatchedExtinguishers();
      await loadExtinguishers();
      await loadDashboard();
    } catch (error) {
      console.error("Error updating dispatch status:", error);
      alert("Error updating dispatch status");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
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
      case "pending":
        return "bg-yellow-500";
      case "in_progress":
        return "bg-blue-500";
      case "completed":
        return "bg-green-500";
      case "overdue":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getDispatchStatusColor = (status) => {
    switch (status) {
      case "dispatched":
        return "bg-blue-500";
      case "under_process":
        return "bg-yellow-500";
      case "received":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  const getDispatchStatusText = (status) => {
    switch (status) {
      case "dispatched":
        return "Dispatched";
      case "under_process":
        return "Under Process";
      case "received":
        return "Received";
      default:
        return "None";
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
      case "pending":
        return "Pending";
      case "in_progress":
        return "In Progress";
      case "completed":
        return "Completed";
      case "overdue":
        return "Overdue";
      default:
        return status;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "text-red-400";
      case "medium":
        return "text-yellow-400";
      case "low":
        return "text-green-400";
      default:
        return "text-gray-400";
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
            {["dashboard", "detectors", "extinguishers", "maintenance", "alerts"].map((tab) => (
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
              <div className="flex justify-between items-center mb-4">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="text-sm text-blue-400 hover:text-blue-300"
                >
                  Forgot Password?
                </button>
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

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Reset Password</h2>
            <div className="mb-4">
              <button
                onClick={getResetCode}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 mb-4"
              >
                Get Reset Code
              </button>
            </div>
            <form onSubmit={handleForgotPassword}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Reset Code</label>
                <input
                  type="text"
                  value={resetData.reset_code}
                  onChange={(e) => setResetData({...resetData, reset_code: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">New Password</label>
                <input
                  type="password"
                  value={resetData.new_password}
                  onChange={(e) => setResetData({...resetData, new_password: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Reset Password
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

      {/* Add Maintenance Item Modal */}
      {showAddMaintenance && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Add Maintenance Item</h2>
            <form onSubmit={handleAddMaintenanceItem}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={newMaintenanceItem.name}
                  onChange={(e) => setNewMaintenanceItem({...newMaintenanceItem, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={newMaintenanceItem.description}
                  onChange={(e) => setNewMaintenanceItem({...newMaintenanceItem, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  rows="3"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Priority</label>
                <select
                  value={newMaintenanceItem.priority}
                  onChange={(e) => setNewMaintenanceItem({...newMaintenanceItem, priority: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Assigned To</label>
                <input
                  type="text"
                  value={newMaintenanceItem.assigned_to}
                  onChange={(e) => setNewMaintenanceItem({...newMaintenanceItem, assigned_to: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Due Date</label>
                <input
                  type="date"
                  value={newMaintenanceItem.due_date}
                  onChange={(e) => setNewMaintenanceItem({...newMaintenanceItem, due_date: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddMaintenance(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Item
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

      {/* Edit Maintenance Item Modal */}
      {showEditMaintenance && editingItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Edit Maintenance Item</h2>
            <form onSubmit={handleEditMaintenanceItem}>
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
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={editingItem.description}
                  onChange={(e) => setEditingItem({...editingItem, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  rows="3"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Status</label>
                <select
                  value={editingItem.status}
                  onChange={(e) => setEditingItem({...editingItem, status: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="overdue">Overdue</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Priority</label>
                <select
                  value={editingItem.priority}
                  onChange={(e) => setEditingItem({...editingItem, priority: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Assigned To</label>
                <input
                  type="text"
                  value={editingItem.assigned_to || ''}
                  onChange={(e) => setEditingItem({...editingItem, assigned_to: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Due Date</label>
                <input
                  type="date"
                  value={editingItem.due_date ? editingItem.due_date.split('T')[0] : ''}
                  onChange={(e) => setEditingItem({...editingItem, due_date: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditMaintenance(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Update Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Note Modal */}
      {showAddNote && selectedMaintenanceItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 p-6 rounded-lg w-96">
            <h2 className="text-xl font-bold mb-4">Add Note</h2>
            <form onSubmit={handleAddNote}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Note</label>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
                  rows="4"
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddNote(false)}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Note
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
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
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
              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-400">Pending Maintenance</p>
                    <p className="text-3xl font-bold text-yellow-400">{dashboardData.maintenance.pending}</p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">M</span>
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
              {isAdmin && extinguisherSubTab === "extinguishers" && (
                <button
                  onClick={() => setShowAddExtinguisher(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Add Extinguisher
                </button>
              )}
            </div>
            
            {/* Sub-tabs */}
            <div className="flex space-x-4 border-b border-gray-600">
              <button
                onClick={() => setExtinguisherSubTab("extinguishers")}
                className={`py-2 px-4 ${extinguisherSubTab === "extinguishers" ? "border-b-2 border-red-600 text-red-400" : "text-gray-400"}`}
              >
                Extinguishers
              </button>
              <button
                onClick={() => setExtinguisherSubTab("status")}
                className={`py-2 px-4 ${extinguisherSubTab === "status" ? "border-b-2 border-red-600 text-red-400" : "text-gray-400"}`}
              >
                Current Status
              </button>
            </div>

            {/* Extinguishers Tab */}
            {extinguisherSubTab === "extinguishers" && (
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
                      
                      {/* New Dispatch/Receive Buttons */}
                      <div className="mt-2 flex space-x-2">
                        <button
                          onClick={() => dispatchExtinguisher(extinguisher.id)}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Dispatch
                        </button>
                        <button
                          onClick={() => receiveExtinguisher(extinguisher.id)}
                          className="flex-1 px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                        >
                          Received
                        </button>
                      </div>
                      
                      {isAdmin && (
                        <div className="mt-2 flex space-x-2">
                          <button
                            onClick={() => {
                              setEditingItem(extinguisher);
                              setShowEditExtinguisher(true);
                            }}
                            className="flex-1 px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
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
            )}

            {/* Current Status Tab */}
            {extinguisherSubTab === "status" && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {dispatchedExtinguishers.map((extinguisher) => (
                  <div key={extinguisher.id} className="bg-gray-800 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold">{extinguisher.name}</h3>
                        <p className="text-gray-400">{extinguisher.location}</p>
                      </div>
                      <div className={`w-4 h-4 rounded-full ${getDispatchStatusColor(extinguisher.dispatch_status)}`}></div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Dispatch Status:</span>
                        <span className={`font-medium ${extinguisher.dispatch_status === "received" ? "text-green-400" : extinguisher.dispatch_status === "dispatched" ? "text-blue-400" : "text-yellow-400"}`}>
                          {getDispatchStatusText(extinguisher.dispatch_status)}
                        </span>
                      </div>
                      {extinguisher.dispatch_date && (
                        <div className="flex justify-between text-sm">
                          <span>Dispatch Date:</span>
                          <span>{formatDate(extinguisher.dispatch_date)}</span>
                        </div>
                      )}
                      {extinguisher.received_date && (
                        <div className="flex justify-between text-sm">
                          <span>Received Date:</span>
                          <span>{formatDate(extinguisher.received_date)}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-sm">
                        <span>Last Refill:</span>
                        <span>{formatDate(extinguisher.last_refill)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Next Refill Due:</span>
                        <span>{formatDate(extinguisher.next_refill_due)}</span>
                      </div>
                    </div>
                    
                    {/* Status Change Buttons */}
                    {extinguisher.dispatch_status === "dispatched" && (
                      <div className="mt-4 flex space-x-2">
                        <button
                          onClick={() => updateDispatchStatus(extinguisher.id, "under_process")}
                          className="flex-1 px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                        >
                          Under Process
                        </button>
                        <button
                          onClick={() => updateDispatchStatus(extinguisher.id, "received")}
                          className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Received
                        </button>
                      </div>
                    )}
                    
                    {extinguisher.dispatch_status === "under_process" && (
                      <div className="mt-4 flex space-x-2">
                        <button
                          onClick={() => updateDispatchStatus(extinguisher.id, "received")}
                          className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Received
                        </button>
                      </div>
                    )}
                    
                    {extinguisher.dispatch_status === "received" && (
                      <div className="mt-4 text-center text-green-400 font-medium">
                        ✓ Refill Completed
                      </div>
                    )}
                  </div>
                ))}
                {dispatchedExtinguishers.length === 0 && (
                  <div className="col-span-full text-center text-gray-400 py-8">
                    No dispatched extinguishers
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === "maintenance" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Maintenance Items</h2>
              <button
                onClick={() => setShowAddMaintenance(true)}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Add Maintenance Item
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {maintenanceItems.map((item) => (
                <div key={item.id} className="bg-gray-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{item.name}</h3>
                      <p className="text-gray-400">{item.description}</p>
                    </div>
                    <div className={`w-4 h-4 rounded-full ${getStatusColor(item.status)}`}></div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Status:</span>
                      <span className={`font-medium ${getStatusColor(item.status).replace('bg-', 'text-')}`}>
                        {getStatusText(item.status)}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Priority:</span>
                      <span className={`font-medium ${getPriorityColor(item.priority)}`}>
                        {item.priority.charAt(0).toUpperCase() + item.priority.slice(1)}
                      </span>
                    </div>
                    {item.assigned_to && (
                      <div className="flex justify-between text-sm">
                        <span>Assigned To:</span>
                        <span>{item.assigned_to}</span>
                      </div>
                    )}
                    {item.due_date && (
                      <div className="flex justify-between text-sm">
                        <span>Due Date:</span>
                        <span className={getDaysUntil(item.due_date) <= 0 ? "text-red-400" : ""}>
                          {formatDate(item.due_date)}
                          <span className="text-gray-400"> ({getDaysUntil(item.due_date)} days)</span>
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {/* Notes Section */}
                  {item.notes && item.notes.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium mb-2">Notes:</h4>
                      <div className="max-h-32 overflow-y-auto space-y-2">
                        {item.notes.map((note) => (
                          <div key={note.id} className="bg-gray-700 p-2 rounded text-sm">
                            <p>{note.note}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {formatDateTime(note.created_at)} - {note.created_by}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-4 flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedMaintenanceItem(item);
                        setShowAddNote(true);
                      }}
                      className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Add Note
                    </button>
                    <button
                      onClick={() => {
                        setEditingItem(item);
                        setShowEditMaintenance(true);
                      }}
                      className="flex-1 px-3 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteMaintenanceItem(item.id)}
                      className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
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