import { Component } from "react";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Grid from '@mui/material/Grid';
import { Box } from "@mui/system";


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
    }

    componentDidMount() {
        this.fetchSceneText();
    }

    async handleChange(event) {
        await this.setState({ value: event.target.value });
        this.fetchSceneText();

    }

    async fetchSceneText() {
        const response = await fetch(`http://localhost:8000/content-scene/` + this.props.file.name + `/` + this.state.value, {
            method: 'GET',
        });
        if (response.ok) {
            const data = await response.json();
            let scene_content = data.scene_content;
            let validating_lines = data.validating_lines;
            console.log(data)
            let text = [];
            for (let i = 0; i < scene_content.length; i++) {
                if (validating_lines.includes(i)) {
                    text.push(<span key={'line_' + i} className="highlighted correct-text-display" >{scene_content[i] + '\n'}</span>)
                } else {
                    text.push(<span key={'line_' + i} className="correct-text-display">{scene_content[i] + '\n'}</span>)
                }
            }
            this.setState({
                text: text
            });
        } else {
            throw new Error(
                `This is an HTTP error: The status is ${response.status}`
            );
        }
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
                <Box style={{ maxHeight: 250, overflow: 'auto', background: '#ffffff' }}>
                    <div style={{ padding: '2% 10%', textAlign: 'left' }} className="correct-text-display" >{this.state.text}</div>
                </Box>
            </div>
        );
    }

}

export default SceneDisplayer;
