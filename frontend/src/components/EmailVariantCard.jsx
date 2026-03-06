import React from 'react';
import { Mail } from 'lucide-react';

export default function EmailVariantCard({ variant, segmentName }) {
    return (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 flex flex-col space-y-2">
            <div className="flex items-center space-x-2 text-blue-600 font-bold mb-1">
                <Mail className="w-5 h-5" />
                <span>Variant {variant.variant_label}</span>
            </div>
            <div>
                <span className="text-xs font-semibold text-gray-500 uppercase">Subject</span>
                <p className="text-sm font-medium text-gray-900 mt-1">{variant.subject}</p>
            </div>
            <div className="mt-3 bg-white p-3 rounded border border-gray-100 text-sm text-gray-700 whitespace-pre-wrap shadow-sm">
                {variant.body}
            </div>
        </div>
    );
}
