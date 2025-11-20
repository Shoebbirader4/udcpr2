import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Users, Building2, Shield, Activity, Search, Plus, Edit, Trash2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const AdminPanel = () => {
  const [activeTab, setActiveTab] = useState('users');
  const queryClient = useQueryClient();

  const tabs = [
    { id: 'users', label: 'Users', icon: Users },
    { id: 'tenants', label: 'Tenants', icon: Building2 },
    { id: 'roles', label: 'Roles', icon: Shield },
    { id: 'audit', label: 'Audit Logs', icon: Activity }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4">
          <h1 className="text-3xl font-bold">Admin Panel</h1>
          <p className="mt-2 text-purple-100">Manage users, tenants, roles, and system settings</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="flex border-b">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'border-b-2 border-purple-600 text-purple-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon size={20} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {activeTab === 'users' && <UsersTab />}
          {activeTab === 'tenants' && <TenantsTab />}
          {activeTab === 'roles' && <RolesTab />}
          {activeTab === 'audit' && <AuditTab />}
        </div>
      </div>
    </div>
  );
};

const UsersTab = () => {
  const { data: users, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    }
  });

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">User Management</h2>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 flex items-center gap-2">
          <Plus size={20} />
          Add User
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Name</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Email</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Role</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Status</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {users?.map((user) => (
              <tr key={user._id} className="hover:bg-gray-50">
                <td className="px-4 py-3">{user.name}</td>
                <td className="px-4 py-3">{user.email}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                    {user.role || 'User'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                    Active
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex gap-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Edit size={18} />
                    </button>
                    <button className="text-red-600 hover:text-red-800">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const TenantsTab = () => {
  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Tenant Management</h2>
      <p className="text-gray-600">Manage multi-tenant organizations and their subscriptions</p>
    </div>
  );
};

const RolesTab = () => {
  const roles = [
    { name: 'Super Admin', permissions: 20, users: 2 },
    { name: 'Municipal Officer', permissions: 15, users: 5 },
    { name: 'Architect', permissions: 10, users: 25 },
    { name: 'Developer', permissions: 8, users: 50 },
    { name: 'Auditor', permissions: 12, users: 10 }
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Role Management</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {roles.map((role) => (
          <div key={role.name} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-bold text-lg mb-2">{role.name}</h3>
            <p className="text-sm text-gray-600 mb-1">{role.permissions} permissions</p>
            <p className="text-sm text-gray-600">{role.users} users</p>
          </div>
        ))}
      </div>
    </div>
  );
};

const AuditTab = () => {
  const { data: logs } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/admin/audit-logs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    }
  });

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Audit Logs</h2>
      <div className="space-y-2">
        {logs?.slice(0, 20).map((log, i) => (
          <div key={i} className="p-3 bg-gray-50 rounded-lg flex justify-between items-center">
            <div>
              <p className="font-medium">{log.action}</p>
              <p className="text-sm text-gray-600">{log.user?.email}</p>
            </div>
            <span className="text-sm text-gray-500">
              {new Date(log.timestamp).toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminPanel;
