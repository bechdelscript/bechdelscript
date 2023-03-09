// import logo from './logo.svg';
import './App.css';

import CharacterList from './components/characters_list';
import FileUpload from './components/file_upload';

const obj = {
  "characters": [{
    "name": "marge",
    "gender": "female"
  },
  {
    "name": "homer",
    "gender": "male"
  },
  {
    "name": "lisa",
    "gender": "female"
  }]
}

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
        <div>
          <CharacterList characters={obj.characters} />
        </div>
      </body>
    </div>
  );
}

export default App;