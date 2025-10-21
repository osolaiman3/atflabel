import React from 'react';
import AuthModal from './AuthModal'; // Adjust path if necessary

export default {
  title: 'Modals/AuthModal',
  component: AuthModal,
  argTypes: {
    onAuthSuccess: { action: 'authenticated' }, // Log when authentication is successful
    onClose: { action: 'closed' }, // Log when the modal is closed
  },
  parameters: {
    layout: 'fullscreen', // Use fullscreen layout for modals
  },
};

const Template = (args) => <AuthModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  onAuthSuccess: (token, username) => console.log(`Auth Success: ${username}, Token: ${token}`),
  onClose: () => console.log('Auth Modal closed'), // Explicitly provide onClose
};

export const WithInitialFeedback = Template.bind({});
WithInitialFeedback.args = {
  ...Default.args,
  // You'd need to modify AuthModal to accept an initialFeedback prop
  // For now, this demonstrates how you might set up a story for an error state
  // authFeedback: 'Invalid username or password.',
};

export const LoadingState = Template.bind({});
LoadingState.args = {
  ...Default.args,
  // You'd need to modify AuthModal to accept an isLoading prop
  // For now, this demonstrates how you might set up a story for a loading state
  // isLoading: true,
};