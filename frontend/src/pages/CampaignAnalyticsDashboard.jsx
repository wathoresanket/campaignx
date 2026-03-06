import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { backendClient } from '../api/backendClient';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Activity, Trophy, Clock, Target, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function CampaignAnalyticsDashboard() {
    const { id } = useParams();
    const [runs, setRuns] = useState([]);
    const [insights, setInsights] = useState([]);
    const [timeline, setTimeline] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [runsResp, insightsResp, timelineResp] = await Promise.all([
                    backendClient.get(`/campaigns/${id}/metrics`),
                    backendClient.get(`/campaigns/${id}/insights`),
                    backendClient.get(`/campaigns/${id}/optimization-timeline`),
                ]);
                setRuns(runsResp.data || []);
                setInsights(insightsResp.data || []);
                setTimeline(timelineResp.data?.timeline || []);
            } catch (e) {
                console.error("Dashboard failed to load data", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [id]);

    if (loading) return <div className="p-10 text-center text-gray-500 animate-pulse">Loading Analytics Engine...</div>;

    // Aggregate latest loop metrics for the BarChart
    const latestRun = runs.length > 0 ? runs[runs.length - 1] : null;
    const barChartData = latestRun?.metrics?.map(m => ({
        name: `Seg ${m.segment_id} (Var ${m.variant_id})`,
        openRate: m.open_rate * 100, // Convert to percentage
        clickRate: m.click_rate * 100, // Convert to percentage
    })) || [];

    return (
        <div className="space-y-6">
            <div className="bg-white px-4 py-5 border-b border-gray-200 sm:px-6 shadow rounded-lg mb-6 flex justify-between items-center">
                <div>
                    <h3 className="text-xl leading-6 font-bold text-gray-900 flex items-center">
                        <Activity className="mr-2 h-6 w-6 text-indigo-600" />
                        Live Campaign Analytics Engine
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">Real-time performance metrics and AI insights across segments.</p>
                </div>
            </div>

            {/* Top Level Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bar Chart - Current Performance */}
                <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                        <Target className="mr-2 h-5 w-5 text-blue-500" />
                        Current Loop Performance (%)
                    </h4>
                    <div className="h-72">
                        {barChartData.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={barChartData}>
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#6B7280' }} />
                                    <YAxis tick={{ fontSize: 12, fill: '#6B7280' }} />
                                    <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                    <Legend wrapperStyle={{ paddingTop: '10px' }} />
                                    <Bar dataKey="openRate" name="Open Rate" fill="#60A5FA" radius={[4, 4, 0, 0]} />
                                    <Bar dataKey="clickRate" name="Click Rate" fill="#F87171" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex bg-gray-50 h-full items-center justify-center text-gray-400 rounded">No metrics generated yet</div>
                        )}
                    </div>
                </div>

                {/* Line Chart - Campaign Timeline Evolution */}
                <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                        <Clock className="mr-2 h-5 w-5 text-emerald-500" />
                        Optimization Timeline Evolution
                    </h4>
                    <div className="h-72">
                        {timeline.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={timeline}>
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                                    <XAxis dataKey="run_number" tick={{ fontSize: 12, fill: '#6B7280' }} tickFormatter={(val) => `Loop ${val}`} />
                                    <YAxis tick={{ fontSize: 12, fill: '#6B7280' }} />
                                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                    <Legend wrapperStyle={{ paddingTop: '10px' }} />
                                    <Line type="monotone" dataKey="avg_open_rate" name="Avg Open Rate" stroke="#10B981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                                    <Line type="monotone" dataKey="avg_click_rate" name="Avg Click Rate" stroke="#8B5CF6" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex bg-gray-50 h-full items-center justify-center text-gray-400 rounded">Awaiting loop completion</div>
                        )}
                    </div>
                </div>
            </div>

            {/* Explainable AI Insight System Panel */}
            <div className="mt-8">
                <h4 className="text-xl font-bold text-gray-900 mb-4">Explainable AI Insights</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {insights.map((insight, idx) => (
                        <div key={idx} className="bg-gradient-to-br from-indigo-50 to-white rounded-xl shadow-sm border border-indigo-100 p-6 flex flex-col relative overflow-hidden transition-all hover:shadow-md">
                            <div className="absolute top-0 right-0 p-3">
                                <Trophy className="text-yellow-400 h-8 w-8 opacity-20" />
                            </div>

                            <h5 className="font-bold text-indigo-900 mb-1 text-lg">{insight.segment_name}</h5>
                            <span className="text-xs font-semibold uppercase tracking-wider text-indigo-500 mb-4 block">
                                Top Demographic: {insight.top_segment || 'N/A'}
                            </span>

                            <div className="space-y-4 flex-grow">
                                <div>
                                    <p className="text-xs text-gray-500 uppercase font-semibold">Winning Subject Pattern</p>
                                    <p className="text-sm text-gray-800 bg-white p-2 rounded border border-gray-100 mt-1 italic">"{insight.winning_subject_pattern}"</p>
                                </div>

                                <div className="flex items-center bg-emerald-50 text-emerald-700 p-2 rounded border border-emerald-100">
                                    <Clock className="h-4 w-4 mr-2 flex-shrink-0" />
                                    <span className="text-sm font-medium">Optimal Time: {insight.best_send_time}</span>
                                </div>

                                <div className="bg-white p-3 rounded shadow-sm border border-gray-50">
                                    <p className="text-sm text-gray-700 font-medium leading-relaxed flex items-start">
                                        <ArrowUpRight className="h-4 w-4 text-emerald-500 mr-2 flex-shrink-0 mt-0.5" />
                                        {insight.key_insight}
                                    </p>
                                </div>
                            </div>

                            <div className="mt-5 pt-4 border-t border-indigo-100">
                                <p className="text-xs text-indigo-400 uppercase font-bold mb-2">Next Campaign Recommendation</p>
                                <p className="text-sm text-gray-600 bg-indigo-50/50 p-3 rounded-md border border-indigo-50/50">
                                    {insight.recommendation}
                                </p>
                            </div>
                        </div>
                    ))}
                    {insights.length === 0 && (
                        <div className="col-span-full bg-gray-50 text-gray-500 p-10 text-center rounded-lg border border-dashed border-gray-300">
                            AI insights will generate after campaign MAB optimization completes.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
