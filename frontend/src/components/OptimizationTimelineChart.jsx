/**
 * OptimizationTimelineChart.jsx
 * ─────────────────────────────
 * Recharts line chart showing campaign improvement across optimization runs.
 * X-axis = run number, Y-axis = percentage, two lines for open/click rate.
 */

import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp } from 'lucide-react';

export default function OptimizationTimelineChart({ timeline }) {
    // timeline expected: [{ run_number, avg_open_rate, avg_click_rate, best_variant, status }]

    if (!timeline || timeline.length === 0) {
        return (
            <div className="p-4 text-center text-gray-500 border rounded bg-white">
                No optimization data yet. Runs will appear after campaign execution.
            </div>
        );
    }

    // Convert rates to percentages for display
    const chartData = timeline.map(item => ({
        name: `Run ${item.run_number}`,
        'Open Rate': parseFloat((item.avg_open_rate * 100).toFixed(2)),
        'Click Rate': parseFloat((item.avg_click_rate * 100).toFixed(2)),
        bestVariant: item.best_variant,
    }));

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-100">
            <div className="px-4 py-3 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100 flex items-center">
                <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                <h4 className="text-md font-semibold text-green-900">Optimization Progress</h4>
            </div>
            <div className="p-4">
                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                            <YAxis tickFormatter={(val) => `${val}%`} tick={{ fontSize: 12 }} />
                            <Tooltip
                                formatter={(val) => `${val}%`}
                                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                            />
                            <Legend wrapperStyle={{ paddingTop: '10px' }} />
                            <Line
                                type="monotone"
                                dataKey="Open Rate"
                                stroke="#8b5cf6"
                                strokeWidth={2}
                                dot={{ r: 5 }}
                                activeDot={{ r: 7 }}
                            />
                            <Line
                                type="monotone"
                                dataKey="Click Rate"
                                stroke="#10b981"
                                strokeWidth={2}
                                dot={{ r: 5 }}
                                activeDot={{ r: 7 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                {/* Summary cards below the chart */}
                <div className="mt-4 flex gap-3 flex-wrap">
                    {timeline.map((item) => (
                        <div key={item.run_number} className="bg-gray-50 border border-gray-200 rounded-md px-3 py-2 text-xs">
                            <span className="font-semibold text-gray-700">Run {item.run_number}:</span>{' '}
                            <span className="text-green-700">Click {(item.avg_click_rate * 100).toFixed(1)}%</span>{' · '}
                            <span className="text-purple-700">Open {(item.avg_open_rate * 100).toFixed(1)}%</span>{' · '}
                            <span className="text-blue-600">{item.best_variant}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
