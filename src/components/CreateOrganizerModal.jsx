import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

const CreateOrganizerModal = ({ show, handleClose }) => {
  const [organizerName, setOrganizerName] = useState('');
  const [email, setEmail] = useState('');
  const [currency, setCurrency] = useState('EUR');
  const [timezone, setTimezone] = useState('America/New_York');

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Create Organizer</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          {/* Organizer Name */}
          <Form.Group className="mb-3">
            <Form.Label>Organizer Name *</Form.Label>
            <Form.Control
              type="text"
              placeholder="Awesome Organizer Ltd."
              value={organizerName}
              onChange={(e) => setOrganizerName(e.target.value)}
            />
          </Form.Group>

          {/* Email */}
          <Form.Group className="mb-3">
            <Form.Label>Email</Form.Label>
            <Form.Control
              type="email"
              placeholder="undefined"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </Form.Group>

          {/* Currency */}
          <Form.Group className="mb-3">
            <Form.Label>Currency *</Form.Label>
            <Form.Control
              as="select"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            >
              <option>EUR</option>
              <option>USD</option>
              <option>GBP</option>
              <option>INR</option>
            </Form.Control>
          </Form.Group>

          {/* Timezone */}
          <Form.Group className="mb-3">
            <Form.Label>Timezone *</Form.Label>
            <Form.Control
              as="select"
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
            >
              <option>America/New_York</option>
              <option>America/Los_Angeles</option>
              <option>Europe/London</option>
              <option>Asia/Kolkata</option>
            </Form.Control>
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button
          variant="success"
          onClick={() => {
            console.log('Organizer Created:', { organizerName, email, currency, timezone });
            handleClose();
          }}
        >
          Create Organizer
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default CreateOrganizerModal;