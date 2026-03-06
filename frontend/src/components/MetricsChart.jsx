import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function MetricsChart({ data }) {
    // data expected format: [{ name: 'Segment A - Variant A', openRate: 0.15, clickRate: 0.05 }, ...]

    if (!data || data.length === 0) return <div className="p-4 text-center text-gray-500 border rounded">No metrics data to display.</div>;

    return (
        <div className="h-80 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    margin={{
                        top: 20,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-15} textAnchor="end" height={60} />
                    <YAxis tickFormatter={(val) => `${(val * 100).toFixed(0)}%`} />
                    <Tooltip formatter={(val) => `${(val * 100).toFixed(2)}%`} />
                    <Legend wrapperStyle={{ paddingTop: "20px" }} />
                    <Bar dataKey="openRate" name="Open Rate" fill="#8884d8" />
                    <Bar dataKey="clickRate" name="Click Rate" fill="#82ca9d" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
