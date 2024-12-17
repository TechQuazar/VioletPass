import React, { useState } from "react";
import { Button } from "react-bootstrap";
import CreateEventModal from "./CreateEventModal";

const CreateNewEvent = () => {
  const [showEventModal, setShowEventModal] = useState(false);

  return (
    <>
      <Button
        style={{ backgroundColor: "#28a745", border: "none", borderRadius: "4px" }}
        onClick={() => setShowEventModal(true)}
      >
        Create New Event
      </Button>

      {/* Event Modal */}
      <CreateEventModal
        show={showEventModal}
        handleClose={() => setShowEventModal(false)}
      />
    </>
  );
};

export default CreateNewEvent;