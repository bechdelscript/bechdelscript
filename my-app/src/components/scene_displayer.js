import { Component } from "react";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Grid from '@mui/material/Grid';




class SceneDisplayer extends Component {

    constructor(props) {
        super(props);
        this.state = {
            value: this.props.scenes[0]
        };
    }

    render() {
        const rows = [];
        for (let i = 0; i < this.props.scenes.length; i++) {
            rows.push(
                <MenuItem value={this.props.scenes[i]}>
                    {this.props.scenes[i]}
                </MenuItem>
            );
        }
        return (
            <>
                <Grid container spacing={5} columns={12}>
                    <Grid item="true" xs={6}>Choose a scene :</Grid>
                    <Grid item="true" xs={6} >

                        <InputLabel id="simple-scene-select-label"></InputLabel>
                        <Select
                            labelId="simple-scene-select-label"
                            id="simple-scene-select"
                            value={this.state.value}
                            label="Scenes"
                            onChange={(event) => this.setState({ value: event.target.value })}
                        >
                            {rows}
                        </Select>
                    </Grid>
                </Grid>
                <br />
                <div>
                    {this.state.value}
                </div>
            </>
        );
    }

}

export default SceneDisplayer;
