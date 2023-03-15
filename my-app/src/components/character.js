import React, { Component } from "react";
import GenderSelect from "./gender_select";
import Grid from '@mui/system/Unstable_Grid/Grid';

class Character extends Component {

    render() {
        return (
            <Grid container spacing={5} columns={12}>
                <Grid item xs={3}>{this.props.name}</Grid>
                <Grid item xs={3}>{this.props.gender}</Grid>
                <GenderSelect gender={this.props.gender} handleChange={this.props.handleChange} />
            </Grid>
        )
    }
}

export default Character;