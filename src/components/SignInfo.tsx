import React from 'react';

type SignData = {
  label: string;
  description: string;
  actionTip: string;
};

const SignInfo = ({ sign }: { sign: SignData }) => (
  <div style={{ border: '1px solid #ccc', padding: '1rem', margin: '1rem 0' }}>
    <h2>{sign.label}</h2>
    <p>{sign.description}</p>
    <p><strong>행동 요령:</strong> {sign.actionTip}</p>
  </div>
);

export default SignInfo;
