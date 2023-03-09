// import logo from './logo.svg';
import './App.css';
import React from 'react';

import FileUpload from './components/file_upload';
import Results from "./components/results";

class App extends React.Component {

	constructor(props) {
		super(props);
		this.state = {
			computed_score: null,
			characters: null,
			file: null
		};
	}

	handleUploadFileSelect = (event) => {
		console.log(event.target.files.item(0))
		const newFile = event.target.files.item(0);
		this.setState({
			file: newFile
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
			computed_score: data.computed_score,
			characters: data.characters
		});
	}

	handleGenderChange = async (i, event) => {
		const characters = this.state.characters.slice();
		characters[i].gender = event.target.value;
		console.log(characters[i].gender);
		this.setState({ characters: characters });
	}

	handleCharactersListSubmit = async (event) => {
		event.preventDefault();
		const formData = new FormData();
		formData.append('file_name', this.state.file.name);
		formData.append('characters_list', this.state.characters);
		const response = await fetch("http://localhost:8000/result-with-user-gender-by-title/", {
			method: 'POST',
			body: formData,
		});
		console.log(response);
		// TODO : check response is valid
		const data = await response.json();
		console.log(data);
		this.setState({
			computed_score: data.computed_score,
			characters: data.characters
		});
	}


	render() {
		return (
			<div className="App">
				<header className="App-header">
					{/* <img src={logo} className="App-logo" alt="logo" /> */}
					<p>
						Bechdel Test AI
					</p>
				</header>
				<div>
					<div>
						<FileUpload
							handleFileSelect={this.handleUploadFileSelect}
							handleSubmit={this.handleUploadFileSubmit}
						/>
					</div>
					<div>
						<Results
							characters={this.state.characters}
							computed_score={this.state.computed_score}
							handleChange={this.handleGenderChange}
							handleSubmit={this.handleCharactersListSubmit}
						/>
					</div>
				</div>
			</div>
		);
	}
}

export default App;