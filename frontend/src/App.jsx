import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import CampaignBriefPage from './pages/CampaignBriefPage';
import ApprovalPage from './pages/ApprovalPage';
import DashboardPage from './pages/DashboardPage';
import AgentLogsPage from './pages/AgentLogsPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-blue-600 tracking-tight">Campaign<span className="text-gray-900">X</span></span>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-8">
                <Link to="/" className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">New Campaign</Link>
                <Link to="/logs" className="border-transparent text-gray-500 hover:border-blue-500 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">Agent Logs</Link>
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
          <Route path="/logs" element={<AgentLogsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
