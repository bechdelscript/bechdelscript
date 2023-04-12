import './App.css';
import React from 'react';

import FileUpload from './components/file_upload';
import Parameters from './components/parameters';
import Results from "./components/results";
import Explanation from './components/explanations';
import InformationBox from './components/information_box';
import Footer from './components/footer';

import { Typography, Grid } from '@mui/material';

let url = window.location.origin
if (url.startsWith("http://localhost:")) {
    url = "http://localhost"
}

class App extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            computed_score: null,
            characters: null,
            message_result: null,
            scenes: null,
            file: null,
            user_key: null,
            loading: false,
            error_message: null,
            women_only_in_scene: false,
            whole_discussion_not_about_men: false,
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
        formData.append('only_women_in_whole_scene', this.state.women_only_in_scene);
        formData.append('whole_discussion_not_about_men', this.state.whole_discussion_not_about_men);

        const response = await fetch(url + ":8000/api/upload-script/", {
            method: 'POST',
            body: formData,
        });
        if (response.ok) {
            const data = await response.json();
            await this.setState({
                user_key: data.key
            })
            await this.waitAndRetrieveResults(data.key)
        } else {
            this.setState({ loading: false })
            if (response.status === 422) {
                this.setState({
                    error_message: `Invalid file format : Please verify your file.`
                });
            }
            else {
                this.setState({
                    error_message: `This is an HTTP error: The status is ${response.status}`
                });
            }
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
            );
        }

    }

    delay = (milliseconds) => {
        return new Promise(resolve => {
            setTimeout(resolve, milliseconds);
        });
    }

    waitAndRetrieveResults = async (user_key) => {
        let message = "unavailable";
        while (message === "unavailable") {
            let response = await fetch(url + ":8000/api/result-by-key/" + user_key, {
                method: 'GET',
            });
            if (response.ok) {
                const data = await response.json();
                console.log("data", data)
                let message = data.message;
                if (message === "available") {
                    this.setState({
                        computed_score: data.score,
                        characters: data.chars,
                        message_result: data.message_result,
                        scenes: data.scenes,
                        error_message: null,
                        loading: false
                    });
                    return;
                } else {
                    await this.delay(5000);
                }

            } else {
                this.setState({ loading: false })
                this.setState({
                    error_message: `This is an HTTP error: The status is ${response.status}`
                });
                throw new Error(
                    `This is an HTTP error: The status is ${response.status}`
                );
            }
        }
    }

    handleGenderChange = async (i, event) => {
        const characters = this.state.characters.slice();
        characters[i].gender = event.target.value;
        this.setState({ characters: characters });
    }

    handleCharactersListSubmit = async (event) => {
        event.preventDefault();
        this.setState({ loading: true })
        const response = await fetch(url + ":8000/api/result-with-user-gender-by-key/", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                key: this.state.user_key,
                user_gender: this.state.characters,
                parameters: {
                    only_women_in_whole_scene: this.state.women_only_in_scene,
                    whole_discussion_not_about_men: this.state.whole_discussion_not_about_men,
                }
            })
        });
        if (response.ok) {
            await this.waitAndRetrieveResults(this.state.user_key)
        } else {
            this.setState({ loading: false })
            if (response.status === 422) {
                this.setState({
                    error_message: `Invalid file format : Please verify your file.`
                });
            }
            else {
                this.setState({
                    error_message: `This is an HTTP error: The status is ${response.status}`
                });
            }
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
            );
        }

    }

    handleWomenSwitch = async (event) => {
        let checked = event.target.checked;
        let whole_discussion_not_about_men = this.state.whole_discussion_not_about_men;
        if (!checked & whole_discussion_not_about_men) {
            whole_discussion_not_about_men = false;
        }
        this.setState(
            {
                women_only_in_scene: checked,
                whole_discussion_not_about_men: whole_discussion_not_about_men
            }
        );

    }

    handleDiscussionSwitch = async (event) => {
        let checked = event.target.checked;
        let women_only_in_scene = this.state.women_only_in_scene;
        if (checked & !women_only_in_scene) {
            women_only_in_scene = true;
        }
        this.setState(
            {
                women_only_in_scene: women_only_in_scene,
                whole_discussion_not_about_men: checked
            }
        );

    }

    render() {
        return (
            <div className="App margin-auto">
                <header className="App-header">
                    <Typography variant='h3' className='padding-20px'>Bechdel Script Tester</Typography>
                </header>
                <Grid container spacing={8} className="padding-20px counter-balance">
                    <Grid item xs={4}>
                        <Explanation />
                    </Grid>
                    <Grid item xs={4}>
                        <FileUpload
                            handleFileSelect={this.handleUploadFileSelect}
                            handleSubmit={this.handleUploadFileSubmit}
                            loading={this.state.loading}
                            file={this.state.file}
                            error_message={this.state.error_message}
                        />
                    </Grid>
                    <Grid item xs={4}>
                        <Parameters
                            handleWomenSwitch={this.handleWomenSwitch}
                            checkedWomenSwitch={this.state.women_only_in_scene}
                            handleDiscussionSwitch={this.handleDiscussionSwitch}
                            checkedDiscussionSwitch={this.state.whole_discussion_not_about_men}
                        />
                    </Grid>
                    <InformationBox characters={this.state.characters} loading={this.state.loading} />
                    <Grid item xs={12}>
                        <Results
                            loading={this.state.loading}
                            characters={this.state.characters}
                            message_result={this.state.message_result}
                            scenes={this.state.scenes}
                            computed_score={this.state.computed_score}
                            handleChange={this.handleGenderChange}
                            handleSubmit={this.handleCharactersListSubmit}
                            user_key={this.state.user_key}
                        />
                    </Grid>
                </Grid>
                <footer className="App-footer">
                    <Footer />
                </footer>
            </div>
        );
    }
}

export default App;