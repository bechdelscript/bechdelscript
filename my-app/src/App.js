// import logo from './logo.svg';
import './App.css';

import FileUpload from './components/file_upload';

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
          <FileUpload />
        </div>
      </body>
    </div>
  );
}

export default App;