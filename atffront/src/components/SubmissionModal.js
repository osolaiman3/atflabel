import React, { useState } from 'react';

const SubmissionModal = ({ data, onClose, images, onConfirm, token }) => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submissionError, setSubmissionError] = useState('');

    const handleConfirm = async () => {
        setIsSubmitting(true);
        setSubmissionError('');

        try {
            // Create FormData for multipart/form-data submission
            const formData = new FormData();
            
            // Add text fields
            formData.append('brandName', data.brandName);
            formData.append('productClass', data.productClass);
            formData.append('alcoholContent', data.alcoholContent);
            formData.append('netContents', data.netContents);
            formData.append('netContentsUnit', data.netContentsUnit);
            
            // Add images
            images.forEach((image) => {
                formData.append('images', image);
            });

            // Send to backend
            const response = await fetch('/submit-product', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                setSubmissionError(result.error || 'Submission failed');
                setIsSubmitting(false);
                return;
            }

            // Call onConfirm callback if provided (e.g., to show ResultsModal)
            if (onConfirm) {
                onConfirm(result);
            }
        } catch (error) {
            setSubmissionError('Network error: ' + error.message);
            setIsSubmitting(false);
        }
    };

    const handleEditAgain = () => {
        setSubmissionError('');
        onClose();
    };

    return (
        // Modal Overlay
        <div className="fixed inset-0 z-50 bg-black bg-opacity-70 flex items-center justify-center p-4" onClick={handleEditAgain}>
            {/* Modal Content */}
            <div className="bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md transform transition-all duration-300 scale-100" onClick={e => e.stopPropagation()}>
                
                <h3 className="text-3xl font-extrabold text-amber-500 border-b border-amber-500/50 pb-3 mb-4 text-center">
                    {isSubmitting ? 'Processing Submission' : 'Confirm Submission'}
                </h3>
                
                {!isSubmitting ? (
                    <>
                        <p className="text-gray-300 mb-4 text-sm text-center">
                            Please review the data below before submitting.
                        </p>

                        {/* Error message display */}
                        {submissionError && (
                            <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded text-red-300 text-sm">
                                {submissionError}
                            </div>
                        )}

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
                                <span className="font-semibold">Net Contents:</span>
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

                        {/* Button group */}
                        <div className="mt-6 space-y-3">
                            <button 
                                onClick={handleConfirm}
                                disabled={isSubmitting}
                                className="w-full py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-500 transition duration-200 shadow-md disabled:bg-gray-500 disabled:text-gray-300"
                            >
                                {isSubmitting ? 'Submitting...' : 'Confirm & Submit'}
                            </button>
                            <button 
                                onClick={handleEditAgain}
                                disabled={isSubmitting}
                                className="w-full py-3 bg-amber-500 text-gray-900 font-bold rounded-lg hover:bg-amber-400 transition duration-200 shadow-md disabled:bg-gray-500 disabled:text-gray-300"
                            >
                                Close & Edit Again
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        {/* Processing state */}
                        <div className="space-y-6">
                            <p className="text-gray-300 text-center mb-6">
                                Processing your product submission...
                            </p>

                            {/* Spinner */}
                            <div className="flex justify-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
                            </div>

                            {/* Error message if processing fails */}
                            {submissionError && (
                                <div className="p-3 bg-red-900/50 border border-red-700 rounded text-red-300 text-sm">
                                    {submissionError}
                                </div>
                            )}

                            {/* Cannot close during processing */}
                            <p className="text-gray-400 text-xs text-center italic">
                                Please wait while your submission is processed...
                            </p>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default SubmissionModal