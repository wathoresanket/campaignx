/**
 * DashboardPage.jsx
 * ─────────────────
 * Campaign analytics dashboard showing optimization progress,
 * campaign lifecycle timeline, agent activity feed, and AI insights.
 */

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { backendClient } from '../api/backendClient';
import MetricsChart from '../components/MetricsChart';
import AgentLogsPanel from '../components/AgentLogsPanel';
import OptimizationTimelineChart from '../components/OptimizationTimelineChart';
import CampaignTimeline from '../components/CampaignTimeline';
import { Activity, IterationCcw, Download, Lightbulb } from 'lucide-react';

export default function DashboardPage() {
    const { id } = useParams();
    const [runs, setRuns] = useState([]);
    const [insights, setInsights] = useState([]);
    const [timeline, setTimeline] = useState([]);
    const [logs, setLogs] = useState([]);
    const [campaign, setCampaign] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [runsResp, insightsResp, timelineResp, logsResp, campaignResp] = await Promise.all([
                backendClient.get(`/campaigns/${id}/metrics`),
                backendClient.get(`/campaigns/${id}/insights`).catch(() => ({ data: [] })),
                backendClient.get(`/campaigns/${id}/optimization-timeline`).catch(() => ({ data: { timeline: [] } })),
                backendClient.get(`/campaigns/${id}/logs`).catch(() => ({ data: [] })),
                backendClient.get(`/campaigns/${id}`).catch(() => ({ data: null })),
            ]);
            setRuns(runsResp.data);
            setInsights(insightsResp.data);
            setTimeline(timelineResp.data.timeline || []);
            setLogs(logsResp.data);
            setCampaign(campaignResp.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [id]);

    const exportInsights = () => {
        const payload = {
            campaign_id: id,
            runs: runs,
            insights: insights
        };
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `campaign_${id}_insights.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    if (loading) return <div>Loading dashboard...</div>;

    return (
        <div className="space-y-6">
            <div className="bg-white px-4 py-5 border-b border-gray-200 sm:px-6 shadow rounded-lg mb-6 flex justify-between items-center">
                <div>
                    <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
                        <Activity className="mr-2 h-5 w-5 text-blue-500" />
                        Performance & MAB Optimization Dashboard
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">Live multi-armed bandit optimization results across runs.</p>
                </div>
                <div className="flex bg-blue-50 p-2 rounded items-center">
                    <IterationCcw className="text-blue-600 h-5 w-5 mr-2" />
                    <span className="text-blue-800 font-semibold">{runs.length} / 3 Loops Completed</span>
                </div>
            </div>

            {/* Two-column layout: Campaign Timeline + Agent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Campaign Lifecycle Timeline */}
                <div className="lg:col-span-1">
                    <CampaignTimeline logs={logs} campaignStatus={campaign?.status || 'draft'} />
                </div>
                {/* Live Agent Activity Feed */}
                <div className="lg:col-span-2">
                    <AgentLogsPanel campaignId={id} />
                </div>
            </div>

            {/* Optimization Timeline Chart */}
            <OptimizationTimelineChart timeline={timeline} />

            {/* AI Marketing Insights */}
            {insights.length > 0 && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-lg shadow p-6 mb-6">
                    <div className="flex justify-between items-center mb-4">
                        <h4 className="flex items-center text-xl font-bold text-blue-900">
                            <Lightbulb className="mr-2 h-6 w-6 text-yellow-500" />
                            AI Marketing Insights
                        </h4>
                        <button
                            onClick={exportInsights}
                            className="inline-flex items-center px-4 py-2 border border-blue-300 shadow-sm text-sm font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 transition"
                        >
                            <Download className="mr-2 h-4 w-4" />
                            Export Insights
                        </button>
                    </div>
                    <div className="space-y-4">
                        {insights.map(ins => (
                            <div key={ins.id} className="bg-white p-4 rounded-md shadow-sm border border-blue-100">
                                <span className="font-semibold text-gray-900 block mb-1">Segment: {ins.segment_name}</span>
                                <p className="text-gray-700">{ins.insight_content}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {runs.length === 0 && (
                <div className="text-center p-10 bg-white shadow rounded-lg text-gray-500">
                    Campaign execution and optimization is starting...
                </div>
            )}

            {runs.map((run) => {
                const chartData = run.metrics?.map(m => ({
                    name: `Variant ${m.variant_id} (Seg ${m.segment_id})`,
                    openRate: m.open_rate,
                    clickRate: m.click_rate
                })) || [];

                return (
                    <div key={run.id} className="bg-white shadow rounded-lg overflow-hidden border border-gray-100 mb-6">
                        <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                            <h4 className="text-md font-semibold text-gray-800">Optimization Loop {run.loop_index}</h4>
                            <p className="text-xs text-gray-500">Status: {run.status}</p>
                        </div>
                        <div className="p-4">
                            <MetricsChart data={chartData} />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
