import React, { Component } from 'react';

function Dropdown() {
  return (
    <div className="dropdown-offset">
      <div className="dropdown">
        <table>
          <tr>
            <td>H</td>
            <td>L</td>
          </tr>
        </table>
      </div>
    </div>
  )
}

export default function Annotatable({ text="", preset=null }) {
  return (
    <div className={`annotatable ${text ? '' : 'empty'} ${preset ? 'disabled' : ''}`}>
      {text ? text : <React.Fragment> &nbsp; </React.Fragment>}
      <div className="box">
        <div className="box-content">{preset}</div>
        {preset ? // Only allow for a dropdown if the value is editable (no preset).
          '' : <Dropdown />}
      </div>
    </div>
  )
}
