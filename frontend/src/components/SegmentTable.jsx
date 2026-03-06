/**
 * SegmentTable.jsx
 * ────────────────
 * Displays campaign segments in a table with expandable
 * "Segment Intelligence" rows that show AI-generated explanations.
 */

import React, { useState, useEffect } from 'react';
import { backendClient } from '../api/backendClient';
import { ChevronDown, ChevronRight, Brain } from 'lucide-react';

export default function SegmentTable({ segments, campaignId }) {
    const [expandedSegments, setExpandedSegments] = useState({});
    const [intelligence, setIntelligence] = useState({});
    const [loadingIntel, setLoadingIntel] = useState(false);

    if (!segments || segments.length === 0) {
        return <p className="text-gray-500 text-sm">No segments generated yet.</p>;
    }

    // Toggle expansion for a segment and fetch intelligence if needed
    const toggleSegment = async (segmentName) => {
        const isExpanding = !expandedSegments[segmentName];
        setExpandedSegments(prev => ({ ...prev, [segmentName]: isExpanding }));

        // Fetch segment intelligence if not already loaded
        if (isExpanding && !intelligence[segmentName] && campaignId) {
            setLoadingIntel(true);
            try {
                const resp = await backendClient.get(`/campaigns/${campaignId}/segment-intelligence`);
                const data = resp.data.intelligence || [];
                const intelMap = {};
                data.forEach(item => {
                    intelMap[item.segment_name] = item.intelligence;
                });
                setIntelligence(prev => ({ ...prev, ...intelMap }));
            } catch (e) {
                console.error('Failed to fetch segment intelligence', e);
            } finally {
                setLoadingIntel(false);
            }
        }
    };

    return (
        <div className="overflow-hidden border-b border-gray-200 shadow sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Segment Name
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Audience Size
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-10">
                            {/* Intelligence toggle column */}
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {segments.map((seg) => {
                        const segName = seg.name;
                        const isExpanded = expandedSegments[segName];
                        return (
                            <React.Fragment key={seg.id || seg.name}>
                                {/* Main segment row */}
                                <tr
                                    className="cursor-pointer hover:bg-gray-50 transition-colors"
                                    onClick={() => toggleSegment(segName)}
                                >
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-l border-gray-100">
                                        {segName.replace(/_/g, ' ').toUpperCase()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {seg.customer_count.toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                        {isExpanded
                                            ? <ChevronDown className="h-4 w-4" />
                                            : <ChevronRight className="h-4 w-4" />
                                        }
                                    </td>
                                </tr>

                                {/* Expandable Segment Intelligence row */}
                                {isExpanded && (
                                    <tr>
                                        <td colSpan={3} className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-indigo-400">
                                            <div className="flex items-start space-x-2">
                                                <Brain className="h-5 w-5 text-indigo-500 mt-0.5 flex-shrink-0" />
                                                <div>
                                                    <p className="text-xs font-semibold text-indigo-700 uppercase tracking-wider mb-1">
                                                        Segment Intelligence
                                                    </p>
                                                    {loadingIntel && !intelligence[segName] ? (
                                                        <p className="text-sm text-gray-500 animate-pulse">Analyzing segment data...</p>
                                                    ) : intelligence[segName] ? (
                                                        <p className="text-sm text-gray-700 leading-relaxed">{intelligence[segName]}</p>
                                                    ) : (
                                                        <p className="text-sm text-gray-500">Intelligence will be available after campaign execution.</p>
                                                    )}
                                                </div>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </React.Fragment>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
