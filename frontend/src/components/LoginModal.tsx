import React, { useState } from 'react';
import { X, Lock, User, ShieldCheck, Eye, EyeOff } from 'lucide-react';
import { ModalFrame } from './ui/ModalFrame';
import { api } from '../api';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: any, token: string) => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await api.login(username, password);
      localStorage.setItem('campusai_token', data.access_token);
      onLoginSuccess(data, data.access_token);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModalFrame onClose={onClose} label="Administrator sign in" className="login-dialog">
      <div className="p-6">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/10 text-blue-400 rounded-lg border border-blue-500/20">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[var(--ink)]">Faculty Administration</h3>
              <p className="text-xs text-slate-400">Curriculum governance & conflict resolution</p>
            </div>
          </div>
          <button
            aria-label="Close sign in"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-[var(--ink)] hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div role="alert" className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 font-medium">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="admin-username" className="block text-xs font-semibold text-slate-300 mb-1.5">
              Username
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                id="admin-username"
                autoComplete="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full glass-input pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
                required
              />
            </div>
          </div>

          <div>
            <label htmlFor="admin-password" className="block text-xs font-semibold text-slate-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                id="admin-password"
                autoComplete="current-password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full glass-input pl-9 pr-10 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
                required
              />
              <button
                type="button"
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-200"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-[var(--paper)] font-semibold py-2.5 rounded-lg text-xs transition-colors shadow-md shadow-blue-600/30 disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Sign In as Administrator'}
            </button>
          </div>

          <p className="text-[11px] text-center text-slate-500 pt-1">
            Default credentials: <code className="text-slate-300 glass-pill px-1.5 py-0.5 rounded font-mono">admin</code> / <code className="text-slate-300 glass-pill px-1.5 py-0.5 rounded font-mono">admin123</code>
          </p>
        </form>
      </div>
    </ModalFrame>
  );
};

