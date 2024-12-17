import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Card, Row, Col, Button, Modal, Form } from "react-bootstrap";
import QRCode from "qrcode";
import { showLoading } from "react-global-loading";
import apigClient from "./api";

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [selectedSeat, setSelectedSeat] = useState("");
  const [qrCode, setQrCode] = useState("");
  const location = useLocation();
  const { user_id } = location.state || {};

  const formatDate = (dateString) => {
    const options = {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    };
    return new Date(dateString).toLocaleString(undefined, options);
  };

  useEffect(() => {
    const fetchBookings = async () => {
      showLoading(true);
      try {
        const response = await apigClient.getBookingsGet({
          user_id,
        });
        const data = response.data;
        setBookings(data.bookings || []);
      } catch (error) {
        if (error.response && error.response.status === 404) {
          console.error("Bookings not found (404).");
          setBookings([]);
        } else {
          console.error("Error fetching bookings:", error);
        }
      }
      showLoading(false);
    };

    fetchBookings();
  }, [user_id]);

  const handleCancelBooking = async (event_id, payment_id) => {
    setIsLoading(true);
    try {
      await apigClient.cancelPost(
        {},
        {
          user_id,
          event_id,
          payment_id,
        }
      );
      setBookings((prevBookings) =>
        prevBookings.filter((booking) => booking.event_id !== event_id)
      );
    } catch (error) {
      console.error("Error cancelling booking:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleShowQrModal = (booking) => {
    setSelectedBooking(booking);
    setSelectedSeat("");
    setQrCode("");
    setShowModal(true);
  };

  const handleSeatChange = async (seat) => {
    setSelectedSeat(seat);
    if (seat) {
      const data = `${seat}-${selectedBooking.payment_id}`;
      try {
        const qr = await QRCode.toDataURL(data);
        setQrCode(qr);
      } catch (err) {
        console.error("Error generating QR code:", err);
      }
    } else {
      setQrCode("");
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedBooking(null);
    setSelectedSeat("");
    setQrCode("");
  };

  return (
    <div style={{ padding: "2rem",backgroundColor:'white' }}>
      <h2>My Bookings</h2>
      {bookings.length > 0 ? (
        bookings.map((booking, index) => (
          <Card className="mb-4" key={booking.payment_id}>
            <Card.Body>
              <Row>
                <Col md={8}>
                  <h5>{booking.name}</h5>
                  <p>
                    <strong>Venue:</strong> {booking.venue}, {booking.location}
                  </p>
                  <p>
                    <strong>Event Dates:</strong>{" "}
                    {formatDate(booking.start_date)} -{" "}
                    {formatDate(booking.end_date)}
                  </p>
                  <p>
                    <strong>Booking Time:</strong>{" "}
                    {formatDate(booking.booking_time)}
                  </p>
                  <p>
                    <strong>Booked Seats:</strong>{" "}
                    {booking.booked_seats.join(", ")}
                  </p>
                </Col>
                <Col md={4} className="text-md-end">
                  <p>
                    <strong>Booking ID:</strong> {booking.payment_id}
                  </p>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleShowQrModal(booking)}
                  >
                    Show QR Code
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() =>
                      handleCancelBooking(booking.event_id, booking.payment_id)
                    }
                    disabled={isLoading}
                    className="ms-2"
                  >
                    {isLoading ? "Cancelling..." : "Cancel Booking"}
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        ))
      ) : (
        <p>No bookings available.</p>
      )}

      {/* Modal for QR Codes */}
      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>QR Code</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedBooking && (
            <>
              <Form.Group>
                <Form.Label>Select a Seat</Form.Label>
                <Form.Control
                  as="select"
                  value={selectedSeat}
                  onChange={(e) => handleSeatChange(e.target.value)}
                >
                  <option value="">-- Select a Seat --</option>
                  {selectedBooking.booked_seats.map((seat, idx) => (
                    <option key={idx} value={seat}>
                      {seat}
                    </option>
                  ))}
                </Form.Control>
              </Form.Group>
              {qrCode && (
                <div className="text-center mt-4">
                  <img src={qrCode} alt={`QR Code for ${selectedSeat}`} />
                  <p>
                    <strong>Seat:</strong> {selectedSeat}
                  </p>
                </div>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default MyBookings;