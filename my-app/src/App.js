// import logo from './logo.svg';
import './App.css';
import React from 'react';

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
  
class App extends React.Component {

  constructor(props) {
        super(props);
        this.state = {
            computed_score:null,
            characters:null,
            file: null
        };
    }

    handleUploadFileSelect = (event) => {
        console.log(event.target.files.item(0))
        const newFile = event.target.files.item(0);
        this.setState({
            file : newFile
        });
    }

    handleUploadFileSubmit = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        formData.append('file', this.state.file);

        const response = await fetch("http://localhost:8000/upload_script/", {
            method: 'POST',
            body: formData,
        });
        console.log(response);
        // TODO : check response is valid
        const data = await response.json();
        console.log(data);
        this.setState({
            computed_score : data.computed_score,
            characters : data.characters
        });
        
    }

    render() {
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
                    <FileUpload 
                            handleFileSelect={this.handleUploadFileSelect}
                            handleSubmit={this.handleUploadFileSubmit}
                    />
                    <div>{this.state.computed_score}</div>
                </div>
                <div>
                  <CharacterList characters={obj.characters} />
                </div>
              </body>
            </div>
        );
    }
}

export default App;