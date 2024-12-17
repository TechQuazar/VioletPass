import React from 'react';
import { useLocation } from 'react-router-dom';

const PaymentSuccess = () => {
  const { state } = useLocation();
  const { name, eventName, tickets, seats } = state || {};
  console.log('Payemtn succ',state)

  return (
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <h1 style={{ color: '#28a745' }}>Payment Successful!</h1>
      <p style={{ fontSize: '1.2rem' }}>
        Thank you for your booking, <strong>{name || 'User'}</strong>!
      </p>
      <div
        style={{
          margin: '2rem auto',
          padding: '1.5rem',
          border: '1px solid #ccc',
          borderRadius: '8px',
          maxWidth: '500px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        }}
      >
        <h3>Booking Details</h3>
        <p>
          <strong>Event Name:</strong> {eventName || 'N/A'}
        </p>
        <p>
          <strong>Tickets:</strong> {tickets || 'N/A'}
        </p>
        <p>
          <strong>Seats:</strong> {seats?.join(', ') || 'N/A'}
        </p>
      </div>
      <button
        style={{
          marginTop: '1rem',
          padding: '0.5rem 1rem',
          fontSize: '1rem',
          backgroundColor: '#6f42c1',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
        }}
        onClick={() => (window.location.href = '/')}
      >
        Back to Home
      </button>
    </div>
  );
};

export default PaymentSuccess;