import React from 'react';
import SubmissionModal from './SubmissionModal';

export default {
  title: 'Modals/SubmissionModal',
  component: SubmissionModal,
  argTypes: {
    onClose: { action: 'closed' },
    onConfirm: { action: 'confirmed' },
    data: { control: 'object' },
    images: { control: 'object' },
    token: { control: 'text' },
  },
  parameters: {
    layout: 'fullscreen',
  },
};

const Template = (args) => <SubmissionModal {...args} />;

export const BasicConfirmation = Template.bind({});
BasicConfirmation.args = {
  data: {
    brandName: "Awesome Brews",
    productClass: "Beer",
    alcoholContent: "5.5",
    netContents: "12",
    netContentsUnit: "fl oz",
  },
  images: [],
  onClose: () => console.log('SubmissionModal closed'),
  onConfirm: (result) => console.log('Submission confirmed:', result),
  token: 'mock_jwt_token_12345',
};

export const WithMultipleImages = Template.bind({});
WithMultipleImages.args = {
  data: {
    brandName: "Premium Spirits",
    productClass: "Whiskey",
    alcoholContent: "40.0",
    netContents: "750",
    netContentsUnit: "ml",
  },
  images: [
    'https://via.placeholder.com/300/8B4513/FFFFFF?text=Bottle+Front',
    'https://via.placeholder.com/300/8B4513/FFFFFF?text=Bottle+Back',
    'https://via.placeholder.com/300/8B4513/FFFFFF?text=Label',
  ],
  onClose: () => console.log('SubmissionModal closed'),
  onConfirm: (result) => console.log('Submission confirmed:', result),
  token: 'mock_jwt_token_12345',
};

export const WithSingleImage = Template.bind({});
WithSingleImage.args = {
  data: {
    brandName: "Vineyard Select",
    productClass: "Wine",
    alcoholContent: "13.5",
    netContents: "750",
    netContentsUnit: "ml",
  },
  images: ['https://via.placeholder.com/300/722F37/FFFFFF?text=Wine+Label'],
  onClose: () => console.log('SubmissionModal closed'),
  onConfirm: (result) => console.log('Submission confirmed:', result),
  token: 'mock_jwt_token_12345',
};
