import React, { useState } from 'react';

const ResultsModal = ({ data, onClose, images }) => {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    const goToNextImage = () => {
        setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    };

    const goToPreviousImage = () => {
        setCurrentImageIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
    };

    // Helper function to get validation status from the data structure
    const getValidationStatus = (key) => {
        return data?.validations?.[key] || false;
    };

    return (
        // Modal Overlay
        <div className="fixed inset-0 z-50 bg-black bg-opacity-70 flex items-center justify-center p-4" onClick={onClose}>
            {/* Modal Content */}
            <div className="bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all duration-300 scale-100" onClick={e => e.stopPropagation()}>
                
                <h3 className="text-3xl font-extrabold text-amber-500 border-b border-amber-500/50 pb-3 mb-4 text-center">
                    Submission Success
                </h3>
                
                <p className="text-gray-300 mb-4 text-sm text-center">
                    Results
                </p>

                {/* Image Viewer Section */}
                {images && images.length > 0 && (
                    <div className="mt-4 mb-6 p-4 bg-gray-700 rounded-lg flex flex-col items-center">
                        <div className="relative w-full flex items-center justify-center" style={{ height: '200px' }}>
                            {images.length > 1 && (
                                <button
                                    onClick={goToPreviousImage}
                                    className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-gray-600 hover:bg-gray-500 text-white p-2 rounded-full shadow-lg z-10"
                                >
                                    &lt;
                                </button>
                            )}
                            <img
                                src={images[currentImageIndex]}
                                alt={`Result ${currentImageIndex + 1}`}
                                className="max-w-full max-h-full object-contain rounded"
                            />
                            {images.length > 1 && (
                                <button
                                    onClick={goToNextImage}
                                    className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-gray-600 hover:bg-gray-500 text-white p-2 rounded-full shadow-lg z-10"
                                >
                                    &gt;
                                </button>
                            )}
                        </div>
                        {images.length > 1 && (
                            <p className="text-gray-400 text-sm mt-2">
                                {currentImageIndex + 1} / {images.length}
                            </p>
                        )}
                    </div>
                )}

                <div className="space-y-2 text-gray-200">
                    <div className="flex justify-between">
                        <span className="font-semibold">Brand Name:</span>
                        <span className={getValidationStatus('brand_name') ? "text-green-400" : "text-red-400"}>
                            {getValidationStatus('brand_name') ? '✓ Found' : '✗ Not Found'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Product Class:</span>
                        <span className={getValidationStatus('product_class') ? "text-green-400" : "text-red-400"}>
                            {getValidationStatus('product_class') ? '✓ Found' : '✗ Not Found'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Alcohol Content:</span>
                        <span className={getValidationStatus('alcohol_content') ? "text-green-400" : "text-red-400"}>
                            {getValidationStatus('alcohol_content') ? '✓ Found' : '✗ Not Found'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Net Contents:</span>
                        <span className={getValidationStatus('net_contents') ? "text-green-400" : "text-red-400"}>
                            {getValidationStatus('net_contents') ? '✓ Found' : '✗ Not Found'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Government Warning:</span>
                        <span className={getValidationStatus('gov_warn') ? "text-green-400" : "text-red-400"}>
                            {getValidationStatus('gov_warn') ? '✓ Found' : '✗ Not Found'}
                        </span>
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
                    Close & Start New Verification
                </button>
            </div>
        </div>
    );
};

export default ResultsModal;