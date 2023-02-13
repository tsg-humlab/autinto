import React, { Component } from 'react';

export default function Annotatable({ text="", preset=null }) {
  return (
    <div className={`annotatable ${text ? '' : 'empty'} ${preset ? 'disabled' : ''}`}>
      {text ? text : <React.Fragment> &nbsp; </React.Fragment>}
      <div className="box">
        <div className="box-content">{preset}</div>
      </div>
    </div>
  )
}
