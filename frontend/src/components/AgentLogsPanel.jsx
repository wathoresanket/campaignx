/**
 * AgentLogsPanel.jsx
 * ──────────────────
 * Live agent activity feed showing agents working step-by-step.
 * Displays status icons (✔ completed, ⏳ running, ⚠ error) and
 * fade-in animations for new log entries.
 */

import React, { useEffect, useState, useRef } from 'react';
import { backendClient } from '../api/backendClient';
import { Terminal } from 'lucide-react';

// Status icon component — shows different icons based on agent status
function StatusIcon({ status }) {
    if (status === 'completed') return <span className="text-green-400">✔</span>;
    if (status === 'running') return <span className="text-yellow-400 animate-pulse">⏳</span>;
    if (status === 'error') return <span className="text-red-400">⚠</span>;
    return <span className="text-gray-400">●</span>;
}

export default function AgentLogsPanel({ campaignId }) {
    const [logs, setLogs] = useState([]);
    const [prevCount, setPrevCount] = useState(0);
    const scrollRef = useRef(null);

    const fetchLogs = async () => {
        try {
            const resp = await backendClient.get(`/campaigns/${campaignId}/logs`);
            setLogs(resp.data);
        } catch (e) {
            console.error("Failed to fetch logs", e);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 3000);
        return () => clearInterval(interval);
    }, [campaignId]);

    // Auto-scroll to bottom when new logs arrive
    useEffect(() => {
        if (logs.length > prevCount && scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
        setPrevCount(logs.length);
    }, [logs.length]);

    return (
        <div className="bg-gray-900 rounded-lg shadow overflow-hidden font-mono text-sm border border-gray-700">
            <div className="bg-gray-800 px-4 py-3 flex items-center border-b border-gray-700">
                <Terminal className="text-green-400 h-5 w-5 mr-2" />
                <h4 className="text-gray-200 font-semibold">AI Agent Activity</h4>
                {logs.some(l => l.status === 'running') && (
                    <span className="ml-auto text-xs text-yellow-400 animate-pulse">● Live</span>
                )}
            </div>
            <div ref={scrollRef} className="p-4 h-72 overflow-y-auto space-y-2">
                {logs.length === 0 && <span className="text-gray-500">Waiting for agent activity...</span>}
                {logs.map((log, idx) => {
                    // Determine if this is a "new" log entry for animation
                    const isNew = idx >= prevCount - 1;
                    return (
                        <div
                            key={log.id}
                            className="text-gray-300 flex items-start space-x-2"
                            style={{
                                animation: isNew ? 'fadeIn 0.4s ease-in forwards' : 'none',
                            }}
                        >
                            <StatusIcon status={log.status} />
                            <div className="flex-1">
                                <span className="text-blue-400 font-bold">[{log.agent_name}]</span>{' '}
                                <span>{log.action_description || log.reasoning_summary}</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Inline CSS for fade-in animation */}
            <style>{`
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(8px); }
                    to   { opacity: 1; transform: translateY(0); }
                }
            `}</style>
        </div>
    );
}
