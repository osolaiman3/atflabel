import React from 'react';
import ResultsModal from './ResultsModal'; // Adjust path if necessary

export default {
  title: 'Modals/ResultsModal', // How it appears in the Storybook sidebar
  component: ResultsModal,
  argTypes: {
    onClose: { action: 'closed' }, // Log the onClose event
    data: { control: 'object' },
    images: { control: 'object' },
  },
};

// --- Template for stories ---
const Template = (args) => <ResultsModal {...args} />;

// --- Stories (different states of the component) ---

export const SuccessWithAllValidData = Template.bind({});
SuccessWithAllValidData.args = {
  data: {
    brandName: { value: "Awesome Brews", isValid: true },
    productClass: { value: "Beer", isValid: true },
    alcoholContent: { value: "5.5", isValid: true },
    netContents: { value: "12", isValid: true },
    netContentsUnit: { value: "fl oz", isValid: true },
    govWarningPresent: { value: true, isValid: true },
  },
  images: [], // No images for this story
  onClose: () => console.log('Modal closed'),
};

export const WithMixedValidationAndImages = Template.bind({});
WithMixedValidationAndImages.args = {
  data: {
    brandName: { value: "Questionable Spirits", isValid: true },
    productClass: { value: "Wine", isValid: false }, // Invalid
    alcoholContent: { value: "14.0", isValid: true },
    netContents: { value: "750", isValid: false }, // Invalid
    netContentsUnit: { value: "ml", isValid: true },
    govWarningPresent: { value: false, isValid: false }, // Invalid - warning not present
  },
  images: [
    'https://via.placeholder.com/300/0000FF/FFFFFF?text=Image+1', // Example placeholder image
    'https://via.placeholder.com/300/FF0000/FFFFFF?text=Image+2',
    'https://via.placeholder.com/300/00FF00/FFFFFF?text=Image+3',
  ],
  onClose: () => console.log('Modal closed'),
};

export const NoImages = Template.bind({});
NoImages.args = {
  data: {
    brandName: { value: "Awesome Brews", isValid: true },
    productClass: { value: "Beer", isValid: true },
    alcoholContent: { value: "5.5", isValid: true },
    netContents: { value: "12", isValid: true },
    netContentsUnit: { value: "fl oz", isValid: true },
    govWarningPresent: { value: true, isValid: true },
  },
  images: [],
  onClose: () => console.log('Modal closed'),
};

export const OnlyOneImage = Template.bind({});
OnlyOneImage.args = {
  data: {
    brandName: { value: "Awesome Brews", isValid: true },
    productClass: { value: "Beer", isValid: true },
    alcoholContent: { value: "5.5", isValid: true },
    netContents: { value: "12", isValid: true },
    netContentsUnit: { value: "fl oz", isValid: true },
    govWarningPresent: { value: true, isValid: true },
  },
  images: ['https://via.placeholder.com/300/FFFF00/000000?text=Single+Image'],
  onClose: () => console.log('Modal closed'),
};