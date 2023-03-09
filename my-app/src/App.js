// import logo from './logo.svg';
import './App.css';
import React from 'react';

import CharacterList from './components/characters_list';
import FileUpload from './components/file_upload';

const obj = null;
// const obj = {
// 	"characters": [{
// 		"name": "marge",
// 		"gender": "female"
// 	},
// 	{
// 		"name": "homer",
// 		"gender": "male"
// 	},
// 	{
// 		"name": "lisa",
// 		"gender": "female"
// 	}]
// }

class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            computed_score:null,
            characters:null,
            file: null,
            error_message: null
        };
    }

	handleUploadFileSelect = (event) => {
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
        if (response.ok) {
            const data = await response.json();
            console.log(data);
            this.setState({
                computed_score : data.computed_score,
                characters : data.characters,
                error_message : null
            });
        } else {
            this.setState({
                error_message : `This is an HTTP error: The status is ${response.status}`
            });
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
              );
        }
        
    }

	render() {
		let character_list;
		if (this.state.characters) { character_list = <CharacterList characters={this.state.characters} />; }
		else { character_list = null; }
        let computed_score = this.state.computed_score ? `Computed score ${this.state.computed_score}` : '';
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
                        <div>{this.state.error_message}</div>
                        <div>{computed_score}</div>
					</div>
					<div>
						{character_list}
					</div>
				</body>
			</div>
		);
	}
}

export default App;