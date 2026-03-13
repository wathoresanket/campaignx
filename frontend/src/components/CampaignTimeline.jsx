/**
 * CampaignTimeline.jsx
 * ────────────────────
 * Visual vertical timeline showing the full lifecycle of a campaign.
 * Uses system logs to determine which stages are completed, running, or pending.
 */

import React, { useMemo } from 'react';
import { Clock } from 'lucide-react';

// All 9 stages in the campaign lifecycle, mapped to their module names
const LIFECYCLE_STAGES = [
    { key: 'brief', label: 'Campaign Created', module: 'BriefProcessor' },
    { key: 'strategy', label: 'Strategy Generated', module: 'StrategyEngine' },
    { key: 'segments', label: 'Segments Created', module: 'SegmentEngine' },
    { key: 'content', label: 'Email Variants Generated', module: 'ContentEngine' },
    { key: 'approval', label: 'Human Approval', module: null }, // Determined by campaign status
    { key: 'execution', label: 'Campaign Executed', module: 'ExecutionEngine' },
    { key: 'analytics', label: 'Metrics Collected', module: 'AnalyticsEngine' },
    { key: 'optimization', label: 'Optimization Completed', module: 'OptimizationEngine' },
    { key: 'insights', label: 'Insights Generated', module: 'InsightEngine' },
];

export default function CampaignTimeline({ logs = [], campaignStatus = 'draft' }) {
    // Determine which stages are done based on module log presence
    const stageStatuses = useMemo(() => {
        // Build a set of modules that have "completed" logs
        const completedModules = new Set();
        const runningModules = new Set();

        for (const log of logs) {
            if (log.status === 'completed') {
                completedModules.add(log.module_name);
            } else if (log.status === 'running') {
                runningModules.add(log.module_name);
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

            // Check module logs for other stages
            if (stage.module && completedModules.has(stage.module)) {
                return { ...stage, status: 'completed' };
            }
            if (stage.module && runningModules.has(stage.module)) {
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
