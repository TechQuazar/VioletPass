import React,{useState} from 'react';
import Modal from 'react-bootstrap/Modal';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import Button from 'react-bootstrap/Button';
import { useAuth } from "react-oidc-context";


const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1);

const TicketBookingFooter = ({ auth, handleBookTicket }) => {
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleClose = () => setShowLoginModal(false);
  const handleShow = () => setShowLoginModal(true);

  return (
    <>
      <Modal.Footer>
        {auth.isAuthenticated ? (
          <Button variant="success" onClick={handleBookTicket}>
            Book Ticket
          </Button>
        ) : (
          <Button variant="primary" onClick={handleShow}>
            Book Tickets
          </Button>
        )}
      </Modal.Footer>

      {/* Login Modal */}
      <Modal show={showLoginModal} onHide={handleClose} centered>
        <Modal.Header closeButton>
          <Modal.Title>Login Required</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Please log in to book tickets and enjoy our services.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button variant="primary" onClick={() => auth.signinRedirect()}>
            Login
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

const EventModal = ({ event, show, handleClose }) => {
  const navigate = useNavigate(); // Initialize navigate function
  const auth = useAuth()
  if (!event) return null;
  console.log('Event',event)

  const handleBookTicket = () => {
    // Redirect to ticket booking page
    navigate('/book-ticket', { state: { event } }); // Pass event data as state
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>{event.name}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>
          <strong>Description:</strong> {event.description || "Not Available"}
        </p>
        <p>
          <strong>Start Date:</strong>{" "}
          {new Date(event.start_date).toLocaleString("en-US", {
            dateStyle: "long",
            timeStyle: "short",
          }) || "Not Available"}
        </p>
        <p>
          <strong>End Date:</strong>{" "}
          {new Date(event.end_date).toLocaleString("en-US", {
            dateStyle: "long",
            timeStyle: "short",
          }) || "Not Available"}
        </p>
        <p>
          <strong>Tickets Available:</strong>{" "}
          {event.available_tickets || "Not Available"}
        </p>
        <p>
          <strong>Total Tickets:</strong>{" "}
          {event.total_tickets || "Not Available"}
        </p>
      </Modal.Body>
      <TicketBookingFooter auth={auth} handleBookTicket={handleBookTicket} />
      {/* <Modal.Footer>
        <Button variant="success" onClick={handleBookTicket}>
          Book Ticket
        </Button>
      </Modal.Footer> */}
    </Modal>
  );
};

export default EventModal;