import React, { Component } from "react";
import "./App.css";
import Annotatable from "./Annotatable";

class App extends Component {
  render() {
    const startOptions = [
      ["%L", "!%L"],
      ["%H", "!%H"],
      ["%HL", "!%HL"],
    ];
    const wordOptions = [
      ["H*", "!H*"],
      ["H*L", "!H*L"],
      ["L*", "L*H"],
      ["L*HL", "L*!HL"],
      ["H*LH", "∅"],
    ];
    const endOptions = [["L%"], ["H%"], ["%"]];
    return (
      <div className="App">
        <Annotatable preset="%L" />
        <Annotatable options={wordOptions} text="Dat" /> weet ik{" "}
        <Annotatable options={wordOptions} text="ook" /> niet
        <Annotatable options={endOptions} />
        <Annotatable options={[["H", "L"], ["∅", ""]]} text="zei de" />
        <span style={{whiteSpace: 'nowrap'}}>
          traploper
        <Annotatable options={endOptions} />
        </span>
      </div>
    );
  }
}

export default App;
