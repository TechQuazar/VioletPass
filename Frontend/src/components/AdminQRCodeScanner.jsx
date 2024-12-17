import React, { useState } from "react";
import { Container, Row, Col, Alert, Button } from "react-bootstrap";
import { QrReader } from "react-qr-reader";
// import apigClient from "./api.js;" // Import your API client
import apigClient from './api'

const AdminQRCodeScanner = () => {
  const [scannedData, setScannedData] = useState("");
  const [isCameraActive, setIsCameraActive] = useState(false); // Toggle camera state
  const [showAlert, setShowAlert] = useState(false); // Control alert visibility
  const [alertVariant, setAlertVariant] = useState("success"); // Alert type
  const [alertText, setAlertText] = useState(""); // Alert message

  const handleScan = async (result, error) => {
    if (result) {
      // const [seat_no, payment_id] = scannedData.split("-");
      
      const [seat_no, ...paymentParts] = result.text.split("-");
      const payment_id = paymentParts.join("-");
      setScannedData(result?.text);
      // setScannedData(res)
      console.log('Scanned Text', seat_no,payment_id)
      if (seat_no && payment_id) {
        setIsCameraActive(false);
        callApi(seat_no,payment_id)
      } else {
        setIsCameraActive(false);
        setAlertText("Invalid QR Code format.");
        setAlertVariant("danger");
        setShowAlert(true);
      }
    }
    if (error) {
      console.error(error);
    }
  };

  const callApi = async (seat_no, payment_id) => {
    try {
      // Call API with query parameters
      const params = {payment_id,seat_no}
      const response = await apigClient.scanGet(params);
      console.log('RES C',response)
      
      if (response.status === 200) {
        setAlertText(response.data);
        setAlertVariant("success");
      } else if (response.status === 409) {
        setAlertText(response.data);
        setAlertVariant("warning");
      } else if (response.status === 404) {
        setAlertText(response.data);
        setAlertVariant("warning");
      } else {
        setAlertText("Ticket verification failed.");
        setAlertVariant("danger");
      }
    } catch (err) {
      console.error('Err',err);
      setAlertText(err.response.data);
      setAlertVariant("danger");
    }
    setShowAlert(true);
  };


  const toggleCamera = () => {
    setIsCameraActive((prevState) => !prevState); // Toggle the camera
  };

  const dismissAlert = () => {
    setShowAlert(false); // Hide the alert
    setScannedData({}); // Clear scanned data
  };

  return (
    <Container style={{ padding: "2rem" }}>
      <h2 className="text-center">QR Code Scanner</h2>
      <Row className="justify-content-center">
        <Col md={6}>
          {isCameraActive ? (
            <QrReader
              scanDelay={500}
              onResult={handleScan}
              style={{ width: "100%" }}
            />
          ) : (
            <p className="text-center">Camera is off</p>
          )}
          <div className="text-center mt-3">
            <Button variant="primary" onClick={toggleCamera}>
              {isCameraActive ? "Turn Camera Off" : "Turn Camera On"}
            </Button>
          </div>
        </Col>
      </Row>
      <Row className="mt-4">
        <Col>
          {showAlert && (
            <Alert variant={alertVariant} dismissible onClose={dismissAlert}>
              <h5 className="text-center">{alertText}</h5>
            </Alert>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default AdminQRCodeScanner;