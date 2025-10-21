import React, { useState } from 'react';

const ResultsModal = ({ data, onClose, images }) => {
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    const goToNextImage = () => {
        setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
    };

    const goToPreviousImage = () => {
        setCurrentImageIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
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
                        <span className={data.brandName.isValid ? "text-green-400" : "text-red-400"}>{data.brandName.value}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Product Class:</span>
                        <span className={data.productClass.isValid ? "text-green-400" : "text-red-400"}>{data.productClass.value}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Alcohol Content:</span>
                        <span className={data.alcoholContent.isValid ? "text-green-400" : "text-red-400"}>{data.alcoholContent.value} %</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Net Contents (must be &gt; 0):</span>
                        <span className={data.netContents.isValid ? "text-green-400" : "text-red-400"}>{data.netContents.value} {data.netContentsUnit.value}</span>
                    </div>
                    <div className="flex justify-between">
                        <span className="font-semibold">Government Warning Present:</span>
                        <span className={data.govWarningPresent?.isValid ? "text-green-400" : "text-red-400"}>{data.govWarningPresent?.value ? "True" : "False"}</span>
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