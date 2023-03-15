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
            file: null,
            loading: false,
            error_message: null
        };
    }

    handleUploadFileSelect = (event) => {
        const newFile = event.target.files.item(0);
        this.setState({
            file: newFile
        });
    }

    handleUploadFileSubmit = async (event) => {
        event.preventDefault();
        this.setState({ loading: true })
        const formData = new FormData();
        formData.append('file', this.state.file);

        const response = await fetch("http://localhost:8000/upload-script/", {
            method: 'POST',
            body: formData,
        });
        this.setState({ loading: false })
        if (response.ok) {
            const data = await response.json();
            console.log(data);
            this.setState({
                computed_score: data.score,
                characters: data.chars,
                error_message: null
            });
        } else {
            this.setState({
                error_message: `This is an HTTP error: The status is ${response.status}`
            });
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
            );
        }

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
        formData.append('filename', this.state.file.name);
        formData.append('user_gender', this.state.characters);
        let user_gender = {};
        for (let i = 0; i < this.state.characters.length; i++) {
            user_gender[this.state.characters[i].name] = this.state.characters[i].gender;
        }
        const response = await fetch(`http://localhost:8000/result-with-user-gender-by-title/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: this.state.file.name,
                user_gender: user_gender
            })
        });
        console.log(response);
        // TODO : check response is valid
        const data = await response.json();
        console.log(data);
        this.setState({
            computed_score: data.score,
            characters: data.chars
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
                            loading={this.state.loading}
                            file={this.state.file}
                        />
                        <div>{this.state.error_message}</div>
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