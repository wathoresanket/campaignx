import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import CampaignBriefPage from './pages/CampaignBriefPage';
import ApprovalPage from './pages/ApprovalPage';
import DashboardPage from './pages/DashboardPage';
import CampaignAnalyticsDashboard from './pages/CampaignAnalyticsDashboard';
import SystemLogsPage from './pages/SystemLogsPage';
import CampaignsListPage from './pages/CampaignsListPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center gap-3">
                <svg width="36" height="36" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="drop-shadow-sm filter">
                  <path d="M20 20 L80 80 M80 20 L20 80" stroke="url(#logoGradient)" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
                  <circle cx="20" cy="20" r="8" fill="#3b82f6" />
                  <circle cx="80" cy="80" r="8" fill="#8b5cf6" />
                  <circle cx="80" cy="20" r="8" fill="#10b981" />
                  <circle cx="20" cy="80" r="8" fill="#3b82f6" />
                  <circle cx="50" cy="50" r="10" fill="#ffffff" stroke="#4f46e5" strokeWidth="6" />
                  <defs>
                    <linearGradient id="logoGradient" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
                      <stop stopColor="#3b82f6" />
                      <stop offset="0.5" stopColor="#6366f1" />
                      <stop offset="1" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </svg>
                <span className="text-2xl font-extrabold tracking-tight">
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">Campaign</span>
                  <span className="text-gray-900">X</span>
                </span>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                <Link to="/" className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">New Campaign</Link>
                <Link to="/history" className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">Campaign History</Link>
                <Link to="/logs" className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">System Logs</Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="flex-1 w-full max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Routes>
          <Route path="/" element={<CampaignBriefPage />} />
          <Route path="/campaign/:id/approval" element={<ApprovalPage />} />
          <Route path="/campaign/:id/dashboard" element={<DashboardPage />} />
          <Route path="/campaign/:id/analytics" element={<CampaignAnalyticsDashboard />} />
          <Route path="/history" element={<CampaignsListPage />} />
          <Route path="/logs" element={<SystemLogsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
