import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tantml:react-query';
import { Bell, X, Check, Trash2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data: notifications } = useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${API_URL}/notifications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return res.data;
    },
    refetchInterval: 30000 // Poll every 30 seconds
  });

  const markAsReadMutation = useMutation({
    mutationFn: async (notificationId) => {
      const token = localStorage.getItem('token');
      return axios.patch(
        `${API_URL}/notifications/${notificationId}/read`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: async (notificationId) => {
      const token = localStorage.getItem('token');
      return axios.delete(`${API_URL}/notifications/${notificationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['notifications']);
    }
  });

  const unreadCount = notifications?.filter(n => !n.read).length || 0;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
      >
        <Bell size={24} />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-xl z-50 max-h-[600px] overflow-hidden flex flex-col">
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-bold text-lg">Notifications</h3>
              <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-gray-700">
                <X size={20} />
              </button>
            </div>

            <div className="overflow-y-auto flex-1">
              {notifications?.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <Bell className="mx-auto mb-2 text-gray-400" size={48} />
                  <p>No notifications</p>
                </div>
              ) : (
                <div className="divide-y">
                  {notifications?.map((notification) => (
                    <div
                      key={notification._id}
                      className={`p-4 hover:bg-gray-50 ${!notification.read ? 'bg-blue-50' : ''}`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{notification.title}</h4>
                        <div className="flex gap-1">
                          {!notification.read && (
                            <button
                              onClick={() => markAsReadMutation.mutate(notification._id)}
                              className="text-blue-600 hover:text-blue-800"
                              title="Mark as read"
                            >
                              <Check size={18} />
                            </button>
                          )}
                          <button
                            onClick={() => deleteMutation.mutate(notification._id)}
                            className="text-red-600 hover:text-red-800"
                            title="Delete"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{notification.message}</p>
                      <span className="text-xs text-gray-500">
                        {new Date(notification.createdAt).toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default NotificationCenter;
