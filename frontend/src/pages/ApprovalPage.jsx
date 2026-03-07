import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { backendClient } from '../api/backendClient';
import SegmentTable from '../components/SegmentTable';
import EmailVariantCard from '../components/EmailVariantCard';
import AgentLogsPanel from '../components/AgentLogsPanel';
import { CheckCircle, XCircle, Loader2, MessageSquare } from 'lucide-react';

export default function ApprovalPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [campaign, setCampaign] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackText, setFeedbackText] = useState('');
    const [rejecting, setRejecting] = useState(false);

    const fetchCampaign = async () => {
        try {
            const resp = await backendClient.get(`/campaigns/${id}`);
            setCampaign(resp.data);
            if (resp.data.status === 'pending_approval' || resp.data.status === 'approved' || resp.data.status === 'running' || resp.data.status === 'completed') {
                setLoading(false);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchCampaign();
        // Poll while generating
        const interval = setInterval(() => {
            if (campaign?.status === 'generating' || !campaign) {
                fetchCampaign();
            }
        }, 2000);
        return () => clearInterval(interval);
    }, [id, campaign?.status]);

    const handleApprove = async () => {
        try {
            await backendClient.post(`/campaigns/${id}/approve`);
            navigate(`/campaign/${id}/dashboard`);
        } catch (e) {
            alert("Error approving campaign");
        }
    };

    const handleReject = async () => {
        if (!showFeedback) {
            setShowFeedback(true);
            return;
        }
        try {
            setRejecting(true);
            await backendClient.post(`/campaigns/${id}/reject`, {
                feedback: feedbackText || "Rejected — please improve the campaign plan."
            });
            setShowFeedback(false);
            setFeedbackText('');
            setLoading(true);
            // Campaign status will change to 'generating', polling will pick it up
        } catch (e) {
            alert("Error rejecting campaign");
        } finally {
            setRejecting(false);
        }
    };

    if (loading || campaign?.status === 'generating') {
        return (
            <div className="space-y-6">
                <div className="flex flex-col items-center justify-center h-48 space-y-4 bg-white shadow sm:rounded-lg">
                    <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
                    <p className="text-gray-500 font-medium">
                        {campaign?.status === 'generating' && feedbackText
                            ? 'Regenerating campaign plan based on your feedback...'
                            : 'Agents are structuring your campaign plan...'}
                    </p>
                </div>
                <AgentLogsPanel campaignId={id} />
            </div>
        );
    }

    // Once approved or running, redirect
    if (campaign?.status === 'running' || campaign?.status === 'completed') {
        navigate(`/campaign/${id}/dashboard`);
        return null;
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
                <div className="md:flex md:items-center md:justify-between">
                    <div className="flex-1 min-w-0">
                        <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                            Human-in-the-Loop Approval
                        </h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Review segments and variants before execution.
                        </p>
                    </div>
                    <div className="mt-4 flex md:mt-0 md:ml-4 space-x-3">
                        <button
                            onClick={handleReject}
                            disabled={rejecting}
                            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                        >
                            {rejecting ? (
                                <Loader2 className="-ml-1 mr-2 h-5 w-5 text-gray-400 animate-spin" />
                            ) : showFeedback ? (
                                <MessageSquare className="-ml-1 mr-2 h-5 w-5 text-orange-500" />
                            ) : (
                                <XCircle className="-ml-1 mr-2 h-5 w-5 text-red-500" />
                            )}
                            {showFeedback ? 'Submit Feedback & Regenerate' : 'Reject & Edit'}
                        </button>
                        <button
                            onClick={handleApprove}
                            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        >
                            <CheckCircle className="-ml-1 mr-2 h-5 w-5 text-white" />
                            Approve & Execute
                        </button>
                    </div>
                </div>

                {/* Feedback textarea (shown on first reject click) */}
                {showFeedback && (
                    <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg animate-in slide-in-from-top duration-300">
                        <label className="block text-sm font-medium text-amber-800 mb-2">
                            💬 What should the AI improve?
                        </label>
                        <textarea
                            value={feedbackText}
                            onChange={(e) => setFeedbackText(e.target.value)}
                            placeholder="e.g. Make the email tone more formal, shorten the subject lines, add urgency..."
                            className="w-full px-3 py-2 border border-amber-300 rounded-md shadow-sm focus:ring-amber-500 focus:border-amber-500 text-sm"
                            rows={3}
                        />
                        <p className="text-xs text-amber-600 mt-1">
                            Your feedback will be injected into the AI agents' prompts for regeneration.
                        </p>
                    </div>
                )}
            </div>

            <AgentLogsPanel campaignId={id} />

            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="space-y-6">
                    <div className="bg-white shadow sm:rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Target Segments ({campaign?.segments?.length})</h3>
                            <SegmentTable segments={campaign?.segments || []} campaignId={id} />
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-white shadow sm:rounded-lg">
                        <div className="px-4 py-5 sm:p-6">
                            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Generated Email Variants</h3>
                            <div className="space-y-4 max-h-96 overflow-y-auto pr-2">
                                {campaign?.segments?.map(seg => (
                                    <div key={seg.id} className="mb-6">
                                        <h4 className="font-semibold text-gray-700 mb-2 border-b pb-1 text-sm tracking-wide uppercase">{seg.name}</h4>
                                        <div className="grid grid-cols-1 gap-4">
                                            {seg.variants?.map(v => (
                                                <EmailVariantCard key={v.id} variant={v} segmentName={seg.name} />
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
