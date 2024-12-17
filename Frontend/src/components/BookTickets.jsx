import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./BookTickets.css";
import apigClient from "./api";
import { useAuth } from "react-oidc-context";

const MAX_TICKET_LIMIT = 5; // Maximum tickets user can select
const USERID = "pranav_1"; // Simulated user ID

const BookTickets = () => {
  const { state } = useLocation(); // Access the passed event
  const { event } = state || {}; // Destructure the event variable
  const auth = useAuth()
  const user_id = auth?.user?.profile?.sub || USERID;
  const [selectedTickets, setSelectedTickets] = useState([]);
  const [loading, setLoading] = useState(false); // Loading state for API call
  const navigate = useNavigate();

  // Sort tickets by seat_no
  const sortTickets = (tickets) => {
    return [...tickets].sort((a, b) => {
      const parseSeat = (seat) => {
        const match = seat.match(/^([A-Z]+)(\d+)$/);
        if (!match) return [0, 0]; // Fallback for unexpected format
        const [_, letters, number] = match;
        const letterValue = letters
          .split("")
          .reduce((acc, char) => acc * 26 + (char.charCodeAt(0) - 64), 0); // Convert letters to a numeric value
        return [letterValue, parseInt(number, 10)];
      };

      const [aRow, aCol] = parseSeat(a.seat_no);
      const [bRow, bCol] = parseSeat(b.seat_no);

      return aRow === bRow ? aCol - bCol : aRow - bRow;
    });
  };

  // Group sorted tickets into rows of 10
  const groupTickets = (tickets) => {
    const sortedTickets = sortTickets(tickets);
    const rows = [];
    const seatsPerRow = 10;

    for (let i = 0; i < sortedTickets.length; i += seatsPerRow) {
      rows.push(sortedTickets.slice(i, i + seatsPerRow)); // Create rows of 10 tickets
    }

    return rows;
  };

  const ticketRows = event?.seats ? groupTickets(event.seats) : [];

  // Handle ticket click
  const handleTicketClick = (ticket) => {
    if (selectedTickets.find((t) => t.seat_no === ticket.seat_no)) {
      setSelectedTickets((prev) =>
        prev.filter((t) => t.seat_no !== ticket.seat_no)
      );
    } else {
      if (selectedTickets.length < MAX_TICKET_LIMIT) {
        setSelectedTickets((prev) => [...prev, ticket]);
      } else {
        alert(`You can only select up to ${MAX_TICKET_LIMIT} tickets!`);
      }
    }
  };

  // Handle confirm booking
  const handleConfirmBooking = async () => {
    if (selectedTickets.length === 0) {
      alert("Please select tickets before confirming booking!");
      return;
    }

    setLoading(true);

    try {
      // Step 1: Call /book POST to reserve tickets
      const postBody = {
        event_id: event.event_id,
        user_id: user_id,
        seat_numbers: selectedTickets.map((ticket) => ticket.seat_no),
      };

      console.log("Sending POST request:", postBody);
      const postResponse = await apigClient.bookPost({}, postBody, {});
      const parsedBody =
        typeof postResponse.data.body === "string"
          ? JSON.parse(postResponse.data.body)
          : postResponse.data.body;

      const reserveId = parsedBody.reserve_id || parsedBody.reserveId;

      if (!reserveId) {
        throw new Error("reserveID not found in POST response");
      }

      console.log("Reservation initiated with reserve_id:", reserveId);

      // Step 2: Call /book GET to check reservation status
      const getParams = { reserve_id: reserveId };
      console.log("Sending GET request with params:", getParams);
      const getResponse = await apigClient.bookGet(getParams, {}, {});
      console.log("GET Response:", getResponse);

      const status =
        getResponse.data ||
        (typeof getResponse.data.body === "string"
          ? JSON.parse(getResponse.data.body)?.status
          : getResponse.data.body?.status);

      if (status === "SUCCESS") {
        console.log("Reservation successful!");
        navigate("/payment", {
          state: {
            reservationDetails: {
              event,
              tickets: selectedTickets,
              reserveId,
              
              user_id: user_id,
            },
          },
        });
      } else {
        console.error("Reservation failed with status:", status);
        alert("Reservation failed. Please try again.");
      }
    } catch (error) {
      console.error("Error during reservation process:", error);
      alert("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getTicketClass = (ticket) => {
    if (ticket.status === "locked") return "locked"; // Locked ticket
    if (ticket.status === "booked") return "booked"; // Booked ticket
    if (selectedTickets.find((t) => t.seat_no === ticket.seat_no))
      return "selected"; // Selected ticket
    return ticket.category; // Default category-based styling
  };

  return (
    <div className="container">
      <div className="row justify-content-center">
        {/* Main Seats Section */}
        <h1 className="text-center mb-4 page-heading">
          {event?.name || "Event Name"}
        </h1>

        <div className="col-lg-8 col-md-10 col-sm-12 text-end">
          <div className="grid">
            {/* Render available seats grouped into rows */}
            {ticketRows.length > 0 ? (
              ticketRows.map((row, rowIndex) => (
                <div key={rowIndex} className="row justify-content-center">
                  {row.map((seat) => (
                    <div
                      key={seat.seat_no}
                      className={`ticket ${getTicketClass(seat)}`}
                      onClick={(e) => {
                        const ticket_status = getTicketClass(seat)
                        if (ticket_status === "locked" || ticket_status==='booked') {
                          e.preventDefault();
                          return;
                        }
                        handleTicketClick(seat)}}
                    >
                      {seat.seat_no}
                    </div>
                  ))}
                </div>
              ))
            ) : (
              <p className="text-center">No seats available for this event.</p>
            )}
            <div className="actions text-center mt-4">
              <p>
                Selected Tickets:{" "}
                {selectedTickets.map((t) => t.seat_no).join(", ")}
              </p>
              <button
                className="btn btn-primary"
                onClick={handleConfirmBooking}
                disabled={loading || selectedTickets.length === 0}
              >
                {loading ? "Reserving..." : "Confirm Booking"}
              </button>
            </div>
          </div>
        </div>

        {/* Legend Section */}
        <div className="col-lg-4 col-md-6 col-sm-12">
          <div className="legend">
            <div className="legend-item">
              <span className="ticket basic"></span> Basic
            </div>
            <div className="legend-item">
              <span className="ticket premium"></span> Premium
            </div>
            <div className="legend-item">
              <span className="ticket luxury"></span> Luxury
            </div>
            <div className="legend-item">
              <span className="ticket locked"></span> Locked
            </div>
            <div className="legend-item">
              <span className="ticket booked"></span> Booked
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookTickets;