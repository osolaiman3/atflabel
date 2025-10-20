import React, { useState } from 'react';
import styles from './ProductForm.css'; // Import the CSS Module
import ImageUploader from './ImageUploader.js';
import SubmissionModal from './SubmissionModal.js'

const ProductForm = ({ }) => {
    // Form field state
    const [formData, setFormData] = useState({
        brandName: '',
        productClass: '',
        alcoholContent: 0.0,
        netContents: 0.00,
        netContentsUnit: 'ml',
    });
    // State for feedback/errors (General form errors only)
    const [feedback, setFeedback] = useState('');
    // State to hold validation errors for coloring inputs (red border)
    const [validationErrors, setValidationErrors] = useState({});
    // NEW: State for real-time alcohol content hint/warning
    const [alcoholHint, setAlcoholHint] = useState('');
    
    // State to hold successful submission data for the modal
    const [submissionData, setSubmissionData] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    // State to hold uploaded files
    const [uploadedFiles, setUploadedFiles] = useState([]);


    // Helper function to get error classes
    const getInputClass = (fieldName) => {
        const baseClass = "w-full p-3 border border-gray-600 rounded-lg bg-gray-700 text-white placeholder-gray-500 focus:ring-amber-500 focus:border-amber-500 transition duration-150";
        const errorClass = " border-red-500 focus:border-red-500 focus:ring-red-500";
        return validationErrors[fieldName] ? baseClass + errorClass : baseClass;
    };


    // --- Change Handlers ---
    const handleTextChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        // Clear error on change
        setValidationErrors(prev => ({ ...prev, [name]: false }));
    };

    const handleAlcoholChange = (e) => {
        const value = e.target.value;
        setFormData(prev => ({ ...prev, alcoholContent: value }));
        setValidationErrors(prev => ({ ...prev, alcoholContent: false }));
        
        const floatValue = parseFloat(value);
        const isEmpty = value.trim() === '';

        // Real-time hint/warning logic
        if (!isEmpty && (isNaN(floatValue) || floatValue < 0 || floatValue > 100)) {
            setAlcoholHint('Must be between 0 and 100.');
        } else {
            setAlcoholHint('');
        }
    };

    const handleNetContentsChange = (e) => {
        const value = e.target.value;
        setValidationErrors(prev => ({ ...prev, netContents: false }));

        // Regex allows empty string or numbers with up to two decimal places
        if (value === '' || /^\d+(\.\d{0,2})?$/.test(value)) { 
            setFormData(prev => ({ ...prev, netContents: value }));
            setFeedback('');
        } else {
            // General feedback for invalid characters remains here, as it's less common
            // setFeedback('Net Contents must be a number with up to two decimal places.');
        }
    };

    const handleUnitChange = (e) => {
        setFormData(prev => ({ ...prev, netContentsUnit: e.target.value }));
    };

    const handleImagesChange = (files) => {
        setUploadedFiles(files);
        // Clear image error on successful upload
        if (files.length > 0) {
            setValidationErrors(prev => ({ ...prev, images: false }));
        }
    };


    // --- Submission Handler ---
    const handleSubmit = (e) => {
        // Prevent default browser validation/submission
        e.preventDefault(); 

        let errors = {};
        let hasError = false;
        let submitFeedback = '';

        // 1. Validate required text fields
        if (formData.brandName.trim() === '') { errors.brandName = true; hasError = true; }
        if (formData.productClass.trim() === '') { errors.productClass = true; hasError = true; }

        // 2. Validate Net Contents (must be > 0)
        const netContentsFloat = parseFloat(formData.netContents);
        if (isNaN(netContentsFloat) || netContentsFloat <= 0) {
            errors.netContents = true;
            hasError = true;
        }

        // 3. Validate Alcohol Content (Final check)
        const alcoholStr = formData.alcoholContent.toString().trim();
        const alcohol = parseFloat(alcoholStr);
        
        // Alcohol must be a non-empty string that parses to a valid number in the range [0, 100]
        if (alcoholStr === '' || isNaN(alcohol) || alcohol < 0 || alcohol > 100) {
             errors.alcoholContent = true;
             hasError = true;
        }

        // 4. Validate required image upload
        if (uploadedFiles.length === 0) {
            errors.images = true;
            hasError = true;
        }

        setValidationErrors(errors);

        if (hasError) {
            submitFeedback = 'Error: Please correct the fields marked in red.';
            setFeedback(submitFeedback);
            return;
        }

        // --- SUCCESS PATH ---
        const dataToSubmit = {
            ...formData,
            alcoholContent: parseFloat(alcohol.toFixed(1)),
            netContents: netContentsFloat,
        };

        console.log('Form Submitted!', dataToSubmit, 'with', uploadedFiles.length, 'images.');
        
        // Success: store data, reset validation, and open modal
        setSubmissionData(dataToSubmit);
        setIsModalOpen(true);
        setFeedback('Success! Product data submitted.'); 
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSubmissionData(null);
        setFormData(prev => ({...prev, brandName: '', productClass: '', alcoholContent: 0.0, netContents: 0.00})); // Reset form for new entry
        setUploadedFiles([]);
        setValidationErrors({});
    };

    // Tailwind Class Helpers for consistency
    const labelClasses = "block text-sm font-medium text-gray-300 mb-1";
    const submitButtonClasses = "w-full py-3 bg-amber-500 text-gray-900 font-bold rounded-lg hover:bg-amber-400 transition duration-200 shadow-md"; 

    return (
        // Wrapper for Form and Uploader. Increased max-w to accommodate side-by-side content.
        <div className="max-w-6xl w-full mx-auto p-6 bg-gray-800 rounded-xl shadow-2xl mt-8">
            <h2 className="text-3xl font-extrabold text-amber-500 mb-6 text-center">New Product Registration</h2>

            {/* Feedback Message (Now only for general submit errors/success) */}
            {feedback && (
                <p className={`p-3 mb-4 rounded-lg text-sm text-center font-semibold 
                    ${feedback.startsWith('Error') 
                        ? 'bg-red-900/50 text-red-300 border border-red-700' 
                        : 'bg-green-900/50 text-green-300 border border-green-700'}`
                }>
                    {feedback}
                </p>
            )}

            <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-6" noValidate>
                
                {/* === SIDE-BY-SIDE CONTENT for LG screens, STACKED for mobile === */}
                <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                    
                    {/* 1. Form Fields Section (3/5 width on desktop, full width on mobile) */}
                    <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                        
                        {/* 1. Brand Name (Full width on small screens, one column on desktop) */}
                        <div className="md:col-span-2">
                            <label htmlFor="brandName" className={labelClasses}>Brand Name</label>
                            <input
                                id="brandName"
                                type="text"
                                name="brandName"
                                value={formData.brandName}
                                onChange={handleTextChange}
                                className={getInputClass('brandName')}
                            />
                        </div>

                        {/* 2. Product Class/Type */}
                        <div>
                            <label htmlFor="productClass" className={labelClasses}>Product Class/Type</label>
                            <input
                                id="productClass"
                                type="text"
                                name="productClass"
                                value={formData.productClass}
                                onChange={handleTextChange}
                                className={getInputClass('productClass')}
                            />
                        </div>

                        {/* 3. Alcohol Content (Now with local hint/warning) */}
                        <div>
                            <label htmlFor="alcoholContent" className={labelClasses}>
                                Alcohol Content (%)
                            </label>
                            <input
                                id="alcoholContent"
                                type="number"
                                name="alcoholContent"
                                value={formData.alcoholContent}
                                onChange={handleAlcoholChange}
                                step="0.1"
                                placeholder="e.g., 40.0"
                                className={getInputClass('alcoholContent')}
                            />
                            {/* Conditional hint/warning display */}
                            {alcoholHint ? (
                                <p className="text-xs mt-1 text-red-400 font-medium">
                                    {alcoholHint}
                                </p>
                            ) : (
                                <p className="text-xs mt-1 text-gray-500">
                                    (Value must be between 0 and 100)
                                </p>
                            )}
                        </div>

                        {/* 4. Net Contents (Addressing layout issue: input and selector side-by-side) */}
                        <div className="md:col-span-2">
                            <label htmlFor="netContents" className={labelClasses}>
                                Net Contents (must be &gt; 0)
                            </label>
                            <div className="flex space-x-2">
                                {/* Number Field - takes up most of the space */}
                                <input
                                    id="netContents"
                                    type="text" // Using text for better decimal control
                                    name="netContents"
                                    value={formData.netContents}
                                    onChange={handleNetContentsChange}
                                    className={getInputClass('netContents') + " flex-grow"}
                                />

                                {/* Drop Down - fixed width/padding to match input height */}
                                <select
                                    name="netContentsUnit"
                                    value={formData.netContentsUnit}
                                    onChange={handleUnitChange}
                                    className={getInputClass('netContents') + " w-24"} // Fixed width for selector
                                >
                                    <option value="ml">ml</option>
                                    <option value="fl oz">fl oz</option>
                                    <option value="L">L</option>
                                </select>
                            </div>
                        </div>
                    </div> 
                    {/* End of Form Fields Section */}

                    {/* 2. Image Uploader Section (2/5 width on desktop, full width on mobile) */}
                    <div className="lg:col-span-2">
                        <ImageUploader onImagesChange={handleImagesChange} hasError={validationErrors.images} />
                    </div>
                    {/* End of Image Uploader Section */}

                </div>
                {/* === END SIDE-BY-SIDE CONTENT === */}

                {/* Submit Button (Spans the full width of the wrapper) */}
                <button
                    type="submit"
                    className={submitButtonClasses + " mt-2"}
                >
                    Submit Product
                </button>
            </form>

            {/* Submission Modal - Rendered conditionally */}
            {isModalOpen && submissionData && (
                <SubmissionModal 
                    data={submissionData} 
                    onClose={closeModal} 
                    images={uploadedFiles}
                />
            )}
        </div>
    );
}
export default ProductForm;