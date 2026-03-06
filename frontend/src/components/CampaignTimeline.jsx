/**
 * CampaignTimeline.jsx
 * ────────────────────
 * Visual vertical timeline showing the full lifecycle of a campaign.
 * Uses agent logs to determine which stages are completed, running, or pending.
 */

import React, { useMemo } from 'react';
import { Clock } from 'lucide-react';

// All 9 stages in the campaign lifecycle, mapped to their agent names
const LIFECYCLE_STAGES = [
    { key: 'brief', label: 'Campaign Created', agent: 'CampaignBriefAgent' },
    { key: 'strategy', label: 'Strategy Generated', agent: 'StrategyAgent' },
    { key: 'segments', label: 'Segments Created', agent: 'SegmentationAgent' },
    { key: 'content', label: 'Email Variants Generated', agent: 'ContentAgent' },
    { key: 'approval', label: 'Human Approval', agent: null }, // Determined by campaign status
    { key: 'execution', label: 'Campaign Executed', agent: 'ExecutionAgent' },
    { key: 'analytics', label: 'Metrics Collected', agent: 'AnalyticsAgent' },
    { key: 'optimization', label: 'Optimization Completed', agent: 'OptimizationAgent' },
    { key: 'insights', label: 'Insights Generated', agent: 'InsightAgent' },
];

export default function CampaignTimeline({ logs = [], campaignStatus = 'draft' }) {
    // Determine which stages are done based on agent log presence
    const stageStatuses = useMemo(() => {
        // Build a set of agents that have "completed" logs
        const completedAgents = new Set();
        const runningAgents = new Set();

        for (const log of logs) {
            if (log.status === 'completed') {
                completedAgents.add(log.agent_name);
            } else if (log.status === 'running') {
                runningAgents.add(log.agent_name);
            }
        }

        return LIFECYCLE_STAGES.map((stage) => {
            // Special handling for approval stage
            if (stage.key === 'approval') {
                if (['approved', 'running', 'completed'].includes(campaignStatus)) {
                    return { ...stage, status: 'completed' };
                } else if (campaignStatus === 'pending_approval') {
                    return { ...stage, status: 'running' };
                }
                return { ...stage, status: 'pending' };
            }

            // Check agent logs for other stages
            if (stage.agent && completedAgents.has(stage.agent)) {
                return { ...stage, status: 'completed' };
            }
            if (stage.agent && runningAgents.has(stage.agent)) {
                return { ...stage, status: 'running' };
            }
            return { ...stage, status: 'pending' };
        });
    }, [logs, campaignStatus]);

    // Status icon renderer
    const StatusIcon = ({ status }) => {
        if (status === 'completed') return <span className="text-green-500 text-lg">✔</span>;
        if (status === 'running') return <span className="text-yellow-500 text-lg animate-pulse">⏳</span>;
        return <span className="text-gray-300 text-lg">○</span>;
    };

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-100">
            <div className="px-4 py-3 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-indigo-100 flex items-center">
                <Clock className="h-5 w-5 text-indigo-600 mr-2" />
                <h4 className="text-md font-semibold text-indigo-900">Campaign Lifecycle</h4>
            </div>
            <div className="p-4">
                <div className="relative">
                    {stageStatuses.map((stage, idx) => (
                        <div key={stage.key} className="flex items-start mb-1 last:mb-0">
                            {/* Vertical connector line */}
                            <div className="flex flex-col items-center mr-3">
                                <div className="w-8 h-8 rounded-full flex items-center justify-center border-2 bg-white"
                                    style={{
                                        borderColor: stage.status === 'completed' ? '#22c55e' :
                                            stage.status === 'running' ? '#eab308' : '#e5e7eb'
                                    }}
                                >
                                    <StatusIcon status={stage.status} />
                                </div>
                                {idx < stageStatuses.length - 1 && (
                                    <div className="w-0.5 h-6"
                                        style={{
                                            backgroundColor: stage.status === 'completed' ? '#22c55e' : '#e5e7eb'
                                        }}
                                    />
                                )}
                            </div>
                            {/* Stage label */}
                            <div className="pt-1">
                                <span className={`text-sm font-medium ${stage.status === 'completed' ? 'text-gray-900' :
                                        stage.status === 'running' ? 'text-yellow-700' : 'text-gray-400'
                                    }`}>
                                    {stage.label}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
