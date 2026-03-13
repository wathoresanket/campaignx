/**
 * SystemLogsPage.jsx
 * ──────────────────
 * Global view of all system execution logs across all campaigns.
 */

import React, { useEffect, useState } from 'react';
import { backendClient } from '../api/backendClient';
import { Terminal } from 'lucide-react';

/** Safely pretty-print a JSON string, falling back to raw text. */
function formatJson(raw) {
    if (!raw) return 'No data';
    try {
        const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
        return JSON.stringify(parsed, null, 2);
    } catch {
        return raw;
    }
}

export default function SystemLogsPage() {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const resp = await backendClient.get('/campaigns/logs');
                setLogs(resp.data);
            } catch (e) {
                console.error(e);
            }
        };
        fetchLogs();
        const intv = setInterval(fetchLogs, 5000);
        return () => clearInterval(intv);
    }, []);

    return (
        <div className="bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 border-b border-gray-200 sm:px-6 flex items-center">
                <Terminal className="h-6 w-6 text-gray-500 mr-3" />
                <h3 className="text-lg leading-6 font-medium text-gray-900">System Execution Logs</h3>
            </div>
            <div className="px-4 py-5 sm:p-6 space-y-6">
                {logs.map((log) => (
                    <div key={log.id} className="bg-gray-50 rounded border border-gray-200 p-4">
                        <div className="flex justify-between items-center border-b border-gray-200 pb-2 mb-3">
                            <div className="flex items-center space-x-2">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                    {log.module_name}
                                </span>
                                <span className="text-xs text-gray-500">Campaign #{log.campaign_id}</span>
                            </div>
                            <span className="text-xs text-gray-400">{new Date(log.timestamp).toLocaleString()}</span>
                        </div>

                        <p className="text-sm font-semibold text-gray-800 mb-2">Logic Summary</p>
                        <p className="text-sm text-gray-600 mb-4">{log.logic_summary}</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <div>
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Input Data</p>
                                <pre className="bg-gray-800 text-green-400 p-3 rounded text-xs overflow-x-auto h-32 whitespace-pre-wrap">
                                    {formatJson(log.input_data)}
                                </pre>
                            </div>
                            <div>
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Output Data</p>
                                <pre className="bg-gray-800 text-blue-400 p-3 rounded text-xs overflow-x-auto h-32 whitespace-pre-wrap">
                                    {formatJson(log.output_data)}
                                </pre>
                            </div>
                            <div>
                                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">External Calls</p>
                                <pre className="bg-gray-800 text-yellow-400 p-3 rounded text-xs overflow-x-auto h-32 whitespace-pre-wrap border border-yellow-700">
                                    {log.external_calls && log.external_calls !== "{}" ? formatJson(log.external_calls) : "No external calls executed"}
                                </pre>
                            </div>
                        </div>
                    </div>
                ))}
                {logs.length === 0 && (
                    <p className="text-sm text-gray-500 text-center py-10">No execution activities logged yet.</p>
                )}
            </div>
        </div>
    );
}
