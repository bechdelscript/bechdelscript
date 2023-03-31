import React from "react";
import { Component } from "react";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Grid from '@mui/material/Grid';
import { Box } from "@mui/system";
import { Button } from "@mui/material";


const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        },
    },
};

class SceneDisplayer extends Component {

    constructor(props) {
        super(props);
        this.state = {
            value: this.props.scenes[0],
            text: "",
        };
        this.myHighlightedLine = React.createRef();
        this.myScrollableDiv = React.createRef();

    }

    async componentDidMount() {
        await this.fetchSceneText();
        // when component is created, center on highlighted line
        this.smoothCenterLineInWindow(true)
    }

    componentDidUpdate(prevProps, prevState) {
        // we want the highlighted line to be centered in the parent div when the component update with a new scene
        // (it didn't work when centerLineInDiv was called in handleChange)

        // text = "" the first time the component is created (the scrolling is then dealt with smoothCenterLineInWindow)
        if (prevState.text !== "") {

            // we make sure the scene was changed (and not something else in the component)
            if (!this.comparePreviousStateTextWithCurrentStateText(prevState.text, this.state.text)) {
                this.centerLineInDiv(false)
            }
        }
    }

    comparePreviousStateTextWithCurrentStateText(previous_text, current_text) {
        if (previous_text.length !== current_text.length) {
            return false;
        }
        for (let i = 0; i < previous_text.length; i++) {
            if (previous_text[i].props.children !== current_text[i].props.children) {
                return false;
            }
        }
        return true;
    }

    async handleChange(event) {
        await this.setState({ value: event.target.value });
        await this.fetchSceneText();

    }

    async fetchSceneText() {
        const response = await fetch(`http://localhost:8000/content-scene/` + this.props.file.name + `/` + this.state.value, {
            method: 'GET',
        });
        if (response.ok) {
            const data = await response.json();
            let scene_content = data.scene_content;
            let validating_lines = data.validating_lines;
            let lines_with_male_words = data.lines_with_male_words;
            console.log(data);
            let text = [];
            let ref_used = false;
            for (let i = 0; i < scene_content.length; i++) {
                if (validating_lines.includes(i)) {
                    // pass ref to the first highlighted line only
                    let ref = null;
                    if (!ref_used) {
                        ref = this.myHighlightedLine;
                        ref_used = true;
                    }
                    let first_non_whitespace_character = scene_content[i].search(/\S|$/);
                    text.push(<span ref={ref} key={'line_' + i + '_whitespace'} className="correct-text-display">{scene_content[i].slice(0, first_non_whitespace_character)}</span>);
                    let marker = first_non_whitespace_character;
                    if (Object.keys(lines_with_male_words).includes(i.toString())) {
                        for (let j = 0; j < lines_with_male_words[i].length; j++) {
                            let buzzword_beginning = lines_with_male_words[i][j][0] + first_non_whitespace_character;
                            let buzzword_ending = lines_with_male_words[i][j][1] + first_non_whitespace_character - 1;
                            text.push(<span key={'line_' + i + '_before_' + j} className="highlighted-valid correct-text-display">{scene_content[i].slice(marker, buzzword_beginning)}</span>);
                            text.push(<span key={'line_' + i + '_' + j} className="highlighted-invalid correct-text-display">{scene_content[i].slice(buzzword_beginning, buzzword_ending)}</span>);
                            marker = buzzword_ending;
                        }
                    }
                    text.push(<span key={'line_' + i + 'ending'} className="highlighted-valid correct-text-display">{scene_content[i].slice(marker) + '\n'}</span>);


                } else {
                    text.push(<span key={'line_' + i} className="correct-text-display">{scene_content[i] + '\n'}</span>);
                }
            }
            await this.setState({
                text: text
            });
        } else {
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
            );
        }
    }

    smoothCenterLineInWindow = () => {
        // center the whole window on the first highlighted line
        if (this.myHighlightedLine.current != null) {
            this.myHighlightedLine.current.scrollIntoView({ block: "center", behavior: "smooth" });
        }
    }

    centerLineInDiv = () => {
        // center the highlighted line in its parent div
        let top_pos = this.myHighlightedLine.current.offsetTop;
        this.myScrollableDiv.current.scrollTop = top_pos - this.myScrollableDiv.current.clientHeight / 2;
    }


    render() {
        const rows = [];
        for (let i = 0; i < this.props.scenes.length; i++) {
            rows.push(
                <MenuItem value={this.props.scenes[i]} key={"Scene number " + i.toString()}>
                    {"Scene number " + this.props.scenes[i].toString()}
                </MenuItem>
            );
        }
        return (
            <div>
                <Grid container spacing={5} columns={12}>
                    <Grid item style={{ margin: 'auto' }} xs={6}>
                        Choose a scene :
                    </Grid>
                    <Grid item xs={6}>
                        <InputLabel id="simple-scene-select-label" ></InputLabel>
                        <Select
                            style={{ width: '100%' }}
                            labelId="simple-scene-select-label"
                            id="simple-scene-select"
                            value={this.state.value}
                            onChange={(e) => this.handleChange(e)}
                            MenuProps={MenuProps}
                        >
                            {rows}
                        </Select>
                    </Grid>
                </Grid>
                <br />
                <Box ref={this.myScrollableDiv} style={{ maxHeight: 250, overflow: 'auto', background: '#ffffff', position: 'relative' }}>
                    <div style={{ padding: '2% 10%', textAlign: 'left' }} className="correct-text-display" >{this.state.text}</div>
                </Box>
                <Button sx={{ m: 1 }} onClick={() => { this.centerLineInDiv(); }}>Center validating lines</Button>
            </div>
        );
    }

}

export default SceneDisplayer;
