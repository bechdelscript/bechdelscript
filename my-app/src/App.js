// import logo from './logo.svg';
import './App.css';

import UploadButton from './components/button';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        {/* <img src={logo} className="App-logo" alt="logo" /> */}
        <p>
          <div>Bechdel Test AI</div>
        </p>
      </header>
      <body>
        <div>
          {/* <Button variant="contained">Show</Button> */}
          <UploadButton />
        </div>
      </body>
    </div>
  );
}

export default App;