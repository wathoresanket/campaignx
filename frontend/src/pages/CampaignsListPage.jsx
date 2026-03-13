import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { backendClient } from '../api/backendClient';
import { History, Layout, ArrowRight, CheckCircle, Clock, Loader2, AlertCircle } from 'lucide-react';

export default function CampaignsListPage() {
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchCampaigns = async () => {
            try {
                const response = await backendClient.get('/campaigns/');
                // Sort by ID descending (most recent first)
                const sorted = (response.data || []).sort((a, b) => b.id - a.id);
                setCampaigns(sorted);
            } catch (err) {
                console.error("Failed to fetch campaigns:", err);
                setError("Could not load campaign history. Please try again.");
            } finally {
                setLoading(false);
            }
        };
        fetchCampaigns();
    }, []);

    const getStatusBadge = (status) => {
        switch (status) {
            case 'completed':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Completed
                    </span>
                );
            case 'approved':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        <Clock className="w-3 h-3 mr-1" />
                        Approved
                    </span>
                );
            case 'pending_approval':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        <AlertCircle className="w-3 h-3 mr-1" />
                        Pending Approval
                    </span>
                );
            case 'generating':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                        System Processing
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {status}
                    </span>
                );
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-20 text-gray-500">
                <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
                <p className="text-lg font-medium">Retrieving campaign history...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="bg-white px-4 py-5 border-b border-gray-200 sm:px-6 shadow rounded-lg mb-6 flex justify-between items-center">
                <div>
                    <h3 className="text-xl leading-6 font-bold text-gray-900 flex items-center tracking-tight">
                        <History className="mr-3 h-6 w-6 text-indigo-500" />
                        Campaign Command History
                    </h3>
                    <p className="mt-1 text-sm text-gray-500 font-medium">Review and monitor previous marketing cycles.</p>
                </div>
                <div className="flex space-x-3">
                    <Link
                        to="/"
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition"
                    >
                        + Start New Campaign
                    </Link>
                </div>
            </div>

            {error ? (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center">
                    <AlertCircle className="mr-2" />
                    {error}
                </div>
            ) : campaigns.length === 0 ? (
                <div className="bg-white shadow rounded-lg p-16 text-center border-2 border-dashed border-gray-200">
                    <Layout className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900">No campaigns found</h3>
                    <p className="mt-1 text-sm text-gray-500">Get started by creating your first strategy-driven campaign brief.</p>
                    <div className="mt-6">
                        <Link
                            to="/"
                            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                        >
                            Create Brief
                        </Link>
                    </div>
                </div>
            ) : (
                <div className="bg-white shadow overflow-hidden rounded-lg border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">ID</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Product</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                                <th scope="col" className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Created</th>
                                <th scope="col" className="relative px-6 py-3">
                                    <span className="sr-only">Actions</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {campaigns.map((camp) => (
                                <tr key={camp.id} className="hover:bg-gray-50 transition border-l-4 border-transparent hover:border-indigo-500">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                                        #{camp.id}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900 capitalize">{camp.product || 'Unknown Product'}</div>
                                        <div className="text-xs text-gray-500 truncate max-w-xs">{camp.brief}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {getStatusBadge(camp.status)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                                        {new Date(camp.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <Link
                                            to={camp.status === 'pending_approval' ? `/campaign/${camp.id}/approval` : `/campaign/${camp.id}/dashboard`}
                                            className="inline-flex items-center text-indigo-600 hover:text-indigo-900 font-bold group"
                                        >
                                            View {camp.status === 'pending_approval' ? 'Approval' : 'Stats'}
                                            <ArrowRight className="ml-1 w-4 h-4 transition-transform group-hover:translate-x-1" />
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
