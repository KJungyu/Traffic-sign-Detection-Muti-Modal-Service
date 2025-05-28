import styled from 'styled-components';

export const AppContainer = styled.div`
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', sans-serif;
`;

export const Section = styled.div`
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
`;

export const ChatPopup = styled.div`
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 320px;
  height: 430px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 1000;
  padding: 20px;
`;
