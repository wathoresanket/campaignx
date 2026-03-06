/**
 * HistoricalLearningPanel.jsx
 * ───────────────────────────
 * Displays accumulated knowledge from past campaigns.
 * Fetches learnings from GET /campaigns/learning and shows them as insight cards.
 */

import React, { useEffect, useState } from 'react';
import { backendClient } from '../api/backendClient';
import { BookOpen, Sparkles } from 'lucide-react';

export default function HistoricalLearningPanel() {
    const [learnings, setLearnings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchLearnings = async () => {
            try {
                const resp = await backendClient.get('/campaigns/learning');
                setLearnings(resp.data.learnings || []);
            } catch (e) {
                console.error('Failed to fetch historical learnings', e);
            } finally {
                setLoading(false);
            }
        };
        fetchLearnings();
    }, []);

    if (loading) {
        return (
            <div className="bg-white shadow rounded-lg p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
        );
    }

    // Confidence badge color mapping
    const confidenceColor = (level) => {
        if (level === 'high') return 'bg-green-100 text-green-800';
        if (level === 'medium') return 'bg-yellow-100 text-yellow-800';
        return 'bg-gray-100 text-gray-600';
    };

    return (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-100 rounded-lg shadow overflow-hidden">
            <div className="px-4 py-3 border-b border-amber-100 flex items-center">
                <BookOpen className="h-5 w-5 text-amber-600 mr-2" />
                <h4 className="text-md font-semibold text-amber-900">Previous Campaign Learnings</h4>
                <Sparkles className="h-4 w-4 text-amber-500 ml-2" />
            </div>
            <div className="p-4 space-y-3">
                {learnings.length === 0 && (
                    <p className="text-sm text-gray-500">No historical data yet. Run campaigns to build learnings.</p>
                )}
                {learnings.map((item, idx) => (
                    <div
                        key={idx}
                        className="bg-white rounded-md border border-amber-100 p-3 flex items-start space-x-3 shadow-sm transition-all hover:shadow-md"
                        style={{ animation: `fadeIn 0.3s ease-in ${idx * 0.1}s both` }}
                    >
                        <span className="text-amber-500 text-lg mt-0.5">🧪</span>
                        <div className="flex-1">
                            <p className="text-sm text-gray-800">{item.learning}</p>
                            {item.confidence && (
                                <span className={`inline-block mt-1 px-2 py-0.5 rounded-full text-xs font-medium ${confidenceColor(item.confidence)}`}>
                                    {item.confidence} confidence
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
