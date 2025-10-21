import React, { useState, useCallback } from 'react';

const ImageUploader = ({ onImagesChange, hasError }) => {
    // State to hold files and their preview URLs
    const [uploadedImages, setUploadedImages] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = React.useRef(null);
    const [imageError, setImageError] = useState('');

    // Limits
    const MAX_IMAGES = process.env.MAX_IMAGES || 1;
    const MAX_SIZE_MB = process.env.MAX_IMAGE_SIZE_MB || 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024; // 5MB in bytes

    const handleFiles = useCallback((files) => {
        const filesArray = Array.from(files).filter(file => file.type.startsWith('image/'));
        let newImages = [...uploadedImages];
        let oversizedFiles = [];
        
        setImageError(''); // Reset image error state

        // 1. Filter files based on size and image limit
        for (let i = 0; i < filesArray.length; i++) {
            const file = filesArray[i];
            
            if (file.size > MAX_SIZE_BYTES) {
                oversizedFiles.push(file.name);
                continue;
            }

            if (newImages.length < MAX_IMAGES) {
                newImages.push({
                    file,
                    previewUrl: URL.createObjectURL(file)
                });
            }
        }
        
        // 2. Update state and notify parent
        setUploadedImages(newImages);
        onImagesChange(newImages.map(i => i.file)); // Notify parent of new files

        // 3. Set feedback messages
        if (oversizedFiles.length > 0) {
            setImageError(`Error: ${oversizedFiles.length} file(s) exceed the ${MAX_SIZE_MB}MB limit.`);
        } else if (filesArray.length > 0 && newImages.length === uploadedImages.length) {
            setImageError(`Error: Maximum of ${MAX_IMAGES} images reached.`);
        }

    }, [uploadedImages, onImagesChange]);

    const handleFileChange = (event) => {
        handleFiles(event.target.files);
        // Clear the input value so the same file can be selected again if needed
        event.target.value = null; 
    };

    const handleRemoveImage = (indexToRemove) => {
        const newImages = uploadedImages.filter((_, index) => index !== indexToRemove);
        setUploadedImages(newImages);
        onImagesChange(newImages.map(i => i.file)); // Update parent
        setImageError(''); // Clear error if successful removal makes space
    }

    // Standard Drag Handlers
    const handleDragOver = (event) => {
        event.preventDefault(); 
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (event) => {
        event.preventDefault();
        setIsDragging(false);
        handleFiles(event.dataTransfer.files);
    };

    const handleDragEnter = (event) => {
        event.preventDefault();
        setIsDragging(true);
    };

    const triggerFileUpload = () => {
        fileInputRef.current.click();
    };

    const baseBorderClass = 'border-gray-600';
    const errorBorderClass = 'border-red-500';
    const imageErrorBorderClass = imageError ? 'border-red-500' : (hasError ? errorBorderClass : baseBorderClass);

    return (
        <div className="flex flex-col h-full">
            <label className="block text-sm font-medium text-gray-300 mb-2">Product Images ({uploadedImages.length}/{MAX_IMAGES})</label>
            
            {/* Drag and Drop Zone */}
            <div
                className={`flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg min-h-64 h-full
                            transition-all duration-300 cursor-pointer 
                            ${isDragging ? 'border-amber-500 bg-gray-700/70' : 'bg-gray-700'}
                            ${imageErrorBorderClass}`} // Error highlight
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDragEnter={handleDragEnter}
                onDrop={handleDrop}
                onClick={triggerFileUpload}
            >
                <input
                    type="file"
                    multiple
                    accept="image/*"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="hidden"
                    disabled={uploadedImages.length >= MAX_IMAGES}
                />
                
                {uploadedImages.length === 0 ? (
                    <div className="text-center text-gray-400">
                        <svg xmlns="http://www.w3.org/2000/svg" className="mx-auto h-8 w-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        <p className="mt-2 text-sm">Drag and drop photos here, or click to browse.</p>
                        <p className="text-xs text-gray-500 mt-1">PNG, JPG, up to {MAX_SIZE_MB}MB</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-3 gap-2 w-full h-full p-1">
                        {uploadedImages.map((image, index) => (
                            <div key={index} className="relative aspect-square rounded-md overflow-hidden shadow-lg border border-gray-600">
                                <img
                                    src={image.previewUrl}
                                    alt={`Preview ${index + 1}`}
                                    className="w-full h-full object-cover"
                                />
                                {/* Remove Button */}
                                <button 
                                    onClick={(e) => { e.stopPropagation(); handleRemoveImage(index); }}
                                    className="absolute top-1 right-1 bg-red-600 hover:bg-red-700 text-white p-1 rounded-full text-xs leading-none transition duration-150 shadow-md"
                                    title="Remove Image"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            
            {/* Image Error/Hint Indicator */}
            {imageError ? (
                <p className="text-xs text-left mt-2 text-red-400 font-medium">
                    {imageError}
                </p>
            ) : uploadedImages.length > 0 && (
                <p className="text-xs text-right mt-2 text-gray-400">
                    Uploaded {uploadedImages.length} of {MAX_IMAGES} images.
                </p>
            )}
        </div>
    );
};

export default ImageUploader;