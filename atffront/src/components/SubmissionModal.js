import React, { useState } from 'react';

const SubmissionModal = ({ data, onClose, images }) => {
    return (
        // Modal Overlay
        <div className="fixed inset-0 z-50 bg-black bg-opacity-70 flex items-center justify-center p-4" onClick={onClose}>
            {/* Modal Content */}
            <div className="bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all duration-300 scale-100" onClick={e => e.stopPropagation()}>
                
                <h3 className="text-3xl font-extrabold text-amber-500 border-b border-amber-500/50 pb-3 mb-4 text-center">
                    Submission Success
                </h3>
                
                <p className="text-gray-300 mb-4 text-sm text-center">
                    This is a preview of the data sent to the backend.
                </p>

                <div className="space-y-2 text-gray-200">
                    <div className="flex justify-between">
                        <span className="font-semibold">Brand Name:</span>
                        <span className="text-amber-300">{data.brandName}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Product Class:</span>
                        <span className="text-amber-300">{data.productClass}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Alcohol Content:</span>
                        <span className="text-amber-300">{data.alcoholContent} %</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Net Contents (must be &gt; 0):</span>
                        <span className="text-amber-300">{data.netContents} {data.netContentsUnit}</span>
                    </div>
                    {/* Image count display */}
                    {images.length > 0 && (
                        <div className="flex justify-between pt-2 border-t border-gray-700 mt-2">
                            <span className="font-semibold">Images Attached:</span>
                            <span className="text-amber-300">{images.length} file(s)</span>
                        </div>
                    )}
                </div>

                <button 
                    onClick={onClose}
                    className="mt-6 w-full py-3 bg-amber-500 text-gray-900 font-bold rounded-lg hover:bg-amber-400 transition duration-200 shadow-md"
                >
                    Close & Start New Registration
                </button>
            </div>
        </div>
    );
};

export default SubmissionModal