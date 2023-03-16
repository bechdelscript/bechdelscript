import React, { Component } from "react";
import GenderSelect from "./gender_select";
import Grid from '@mui/system/Unstable_Grid/Grid';

class Character extends Component {

    render() {
        return (
            <Grid container item="true" xs={6}>
                <Grid item="true" xs={1} ></Grid>
                <Grid item="true" xs={5} className="center-text">{this.props.name}</Grid>
                <GenderSelect gender={this.props.gender} handleChange={this.props.handleChange} />
                <Grid item="true" xs={1} ></Grid>
            </Grid>
        )
    }
}

export default Character;