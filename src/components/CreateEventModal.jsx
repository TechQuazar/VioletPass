import React, { useState } from 'react';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css'; // Import styles for the date picker
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { showLoading } from "react-global-loading";


// eslint-disable-next-line no-undef
var apigClient = apigClientFactory.newClient({
  apiKey: import.meta.env.API_KEY,
});

// Assuming apigClient is initialized in the app
const CreateEventModal = ({ show, handleClose, onEventCreated }) => {
  const navigate = useNavigate(); // Initialize navigate function
  const [organizer, setOrganizer] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [venue, setVenue] = useState("");
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState("");
  const [totalTickets, setTotalTickets] = useState("");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  // Form submit handler
  const handleSubmit = async () => {
    const requestBody = {
      // organizer,
      name,
      description,
      venue,
      location,
      category,
      total_tickets: Number(totalTickets),
      start_date: startDate ? startDate.toISOString() : null,
      end_date: endDate ? endDate.toISOString() : null,
    };

    try {
      showLoading(true)
      const response = await apigClient.eventsPost({}, requestBody, {
        headers: { "Content-Type": "application/json" },
      });
      console.log("Response", response);
      if (response.status == 201) {
        // const createdEvent = await response.json();
        console.log("Event created successfully!");
        alert('Event created successfully!')
        // if (onEventCreated) onEventCreated(createdEvent); // Callback to update parent component
        handleClose(); // Close the modal
      } else {
        console.error("Failed to create event:", response.statusText);
      }
    } catch (error) {
      console.error("Error creating event:", error);
    }finally{
      showLoading(false)
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Create Event</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          {/* Organizer Section */}
          <Form.Group className="mb-3">
            <Form.Label>Who is organizing this event? *</Form.Label>
            <Form.Control
              as="select"
              value={organizer}
              onChange={(e) => setOrganizer(e.target.value)}
            >
              <option>Select organizer</option>
              <option>VioletPass Admin</option>
            </Form.Control>
          </Form.Group>

          {/* Event Name */}
          <Form.Group className="mb-3">
            <Form.Label>Name *</Form.Label>
            <Form.Control
              type="text"
              placeholder="VioletPass Conference 2024"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </Form.Group>

          {/* Description */}
          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Event description here..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Form.Group>

          {/* Venue */}
          <Form.Group className="mb-3">
            <Form.Label>Venue *</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter venue"
              value={venue}
              onChange={(e) => setVenue(e.target.value)}
            />
          </Form.Group>

          {/* Location */}
          <Form.Group className="mb-3">
            <Form.Label>Location *</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </Form.Group>

          {/* Category */}
          <Form.Group className="mb-3">
            <Form.Label>Category *</Form.Label>
            <Form.Control
              as="select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option>Select category</option>
              <option value="music">Music</option>
              <option value="dance">Dance</option>
              <option value="concert">Concert</option>
            </Form.Control>
          </Form.Group>

          {/* Total Tickets */}
          <Form.Group className="mb-3">
            <Form.Label>Total Tickets *</Form.Label>
            <Form.Control
              type="number"
              placeholder="Enter total tickets"
              value={totalTickets}
              onChange={(e) => setTotalTickets(e.target.value)}
            />
          </Form.Group>

          {/* Start Date */}
          <Form.Group className="mb-3">
            <Form.Label>Start Date *</Form.Label>
            <DatePicker
              selected={startDate}
              onChange={(date) => setStartDate(date)}
              dateFormat="dd-MM-yyyy"
              placeholderText="Select a start date"
              className="form-control"
              showMonthDropdown
              showYearDropdown
              dropdownMode="select"
            />
          </Form.Group>

          {/* End Date */}
          <Form.Group className="mb-3">
            <Form.Label>End Date</Form.Label>
            <DatePicker
              selected={endDate}
              onChange={(date) => setEndDate(date)}
              dateFormat="dd-MM-yyyy"
              placeholderText="Select an end date"
              className="form-control"
              showMonthDropdown
              showYearDropdown
              dropdownMode="select"
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Create Event
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default CreateEventModal;
