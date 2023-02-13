import React, { useState } from 'react';

function Dropdown({ open, onSelected, options }) {
  return (
    <div className="dropdown-offset">
      <div className={`dropdown ${open ? 'dropdown-active' : ''}`}>
        <table>
          <tbody>
          {options.map((rowOptions, index) => 
          <tr key={index}>
            {rowOptions.map((option) =>
            <td key={option} onClick={() => onSelected(option)}>{option}</td>
            )}
          </tr>
          )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function Annotatable({ text="", preset=null, options=[] }) {
  const [menuOpened, setMenuOpened] = useState(false)
  const [selectedValue, selectValue] = useState(preset)

  return (
    <div onClick={() => setMenuOpened(open => !open)}
         className={`annotatable ${text ? '' : 'empty'} ${preset ? 'disabled' : ''}`}>
      {text ? text : <React.Fragment> &nbsp; </React.Fragment>}
      <div className="box">
        <div className="box-content">{selectedValue}</div>
        {preset ? // Only allow for a dropdown if the value is editable (no preset).
            '' : <Dropdown options={options} open={menuOpened} onSelected={selectValue} />}
      </div>
    </div>
  )
}
