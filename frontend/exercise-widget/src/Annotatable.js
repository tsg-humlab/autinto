import React, { Component } from 'react';

export default function Annotatable({ text }) {
  return (
    <div className="annotatable">
      {text}
      <div className="box"></div>
    </div>
  )
}
