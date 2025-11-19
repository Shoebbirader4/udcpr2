import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

export default function Register() {
  const navigate = useNavigate();
  const { register, handleSubmit, watch } = useForm();
  const password = watch('password');

  const registerMutation = useMutation({
    mutationFn: (data) => axios.post(
      `${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/auth/signup`,
      data
    ),
    onSuccess: () => {
      alert('Registration successful! Please login.');
      navigate('/login');
    }
  });

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-center">Create Account</h1>
        <p className="text-gray-600 text-center mb-8">
          Join UDCPR Master Platform
        </p>

        <form onSubmit={handleSubmit((data) => registerMutation.mutate(data))} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Full Name</label>
            <input
              type="text"
              {...register('name', { required: true })}
              className="w-full border rounded-lg px-3 py-2"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              {...register('email', { required: true })}
              className="w-full border rounded-lg px-3 py-2"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              {...register('password', { required: true, minLength: 6 })}
              className="w-full border rounded-lg px-3 py-2"
              placeholder="At least 6 characters"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Confirm Password</label>
            <input
              type="password"
              {...register('confirmPassword', { 
                required: true,
                validate: value => value === password || "Passwords don't match"
              })}
              className="w-full border rounded-lg px-3 py-2"
              placeholder="Confirm your password"
            />
          </div>

          {registerMutation.isError && (
            <div className="text-red-600 text-sm">
              {registerMutation.error?.response?.data?.message || 'Registration failed. Please try again.'}
            </div>
          )}

          <button
            type="submit"
            disabled={registerMutation.isPending}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {registerMutation.isPending ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:underline">
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
