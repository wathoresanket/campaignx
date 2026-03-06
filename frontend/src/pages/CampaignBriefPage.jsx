/**
 * CampaignBriefPage.jsx
 * ─────────────────────
 * Landing page for creating new campaigns. Includes voice input
 * and displays historical campaign learnings.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { backendClient } from '../api/backendClient';
import { Play, Mic, MicOff } from 'lucide-react';
import HistoricalLearningPanel from '../components/HistoricalLearningPanel';

export default function CampaignBriefPage() {
    const [brief, setBrief] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const navigate = useNavigate();

    const toggleListening = () => {
        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser. Please use Chrome.');
            return;
        }

        if (isListening) {
            window.speechRecognition?.stop();
            setIsListening(false);
            return;
        }

        const SpeechRecognition = window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            let finalTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            if (finalTranscript) {
                setBrief(prev => prev + " " + finalTranscript.trim());
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            setIsListening(false);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.start();
        window.speechRecognition = recognition;
        setIsListening(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!brief.trim()) return;

        setIsSubmitting(true);
        try {
            const resp = await backendClient.post('/campaigns/start', { brief });
            const campaign = resp.data;
            navigate(`/campaign/${campaign.id}/approval`);
        } catch (error) {
            console.error(error);
            alert("Failed to start campaign.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="space-y-6">
            {/* Campaign Brief Input */}
            <div className="bg-white px-4 py-5 border-b border-gray-200 sm:px-6 shadow rounded-lg">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Start New AI Campaign</h3>
                <p className="mt-1 text-sm text-gray-500">Provide a natural language brief. CampaignX agents will handle the rest.</p>

                <form onSubmit={handleSubmit} className="mt-5 sm:flex sm:items-start flex-col space-y-4">
                    <div className="w-full relative">
                        <textarea
                            rows={5}
                            name="brief"
                            id="brief"
                            className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md border p-3 bg-gray-50 pr-12"
                            placeholder="e.g. Run email campaign for XDeposit offering 1% higher returns. Give 0.25% extra for female senior citizens. Optimize for CTR and Open Rate."
                            value={brief}
                            onChange={(e) => setBrief(e.target.value)}
                            disabled={isSubmitting}
                        />
                        <button
                            type="button"
                            onClick={toggleListening}
                            className={`absolute right-3 top-3 p-2 rounded-full focus:outline-none ${isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'text-gray-400 hover:text-gray-600'}`}
                            title={isListening ? "Stop listening" : "Start Voice Input"}
                        >
                            {isListening ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
                        </button>
                    </div>
                    <button
                        type="submit"
                        disabled={isSubmitting}
                        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-colors"
                    >
                        {isSubmitting ? 'Agents are planning...' : 'Generate Campaign Plan'}
                        {!isSubmitting && <Play className="ml-2 -mr-1 h-4 w-4" aria-hidden="true" />}
                    </button>
                </form>
            </div>

            {/* Historical Campaign Learnings */}
            <HistoricalLearningPanel />
        </div>
    );
}
