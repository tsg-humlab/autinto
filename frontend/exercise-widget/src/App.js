import React, { Component } from 'react';
import './App.css';
import Annotatable from './Annotatable'

class App extends Component {
  render() {
    return (
      <div className="App">
        <Annotatable preset="%L"/>
        <Annotatable text="Dat"/> weet ik <Annotatable text="ook"/> niet <Annotatable text="zei de"/> traploper
        <Annotatable />
      </div>
    );
  }
}

export default App;
